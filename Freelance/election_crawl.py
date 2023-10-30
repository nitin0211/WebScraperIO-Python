import argparse
import base64
import io
import json
import queue
import re
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

import easyocr
import pandas as pd
import requests
from PIL import Image

UID_MATCH = re.compile(r'([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*)')

MAX_WORKERS = 150
reader = easyocr.Reader(['en'])


def get_states():
    return {
        "andaman & nicobar islands": "U01",
        "andhra pradesh": "S01",
        "arunachal pradesh": "S02",
        "assam": "S03",
        "bihar": "S04",
        "chandigarh": "U02",
        "chhattisgarh": "S26",
        "dadra & nagar haveli and daman & diu": "U03",
        "goa": "S05",
        "gujarat": "S06",
        "haryana": "S07",
        "himachal pradesh": "S08",
        "jammu and kashmir": "U08",
        "jharkhand": "S27",
        "karnataka": "S10",
        "kerala": "S11",
        "ladakh": "U09",
        "lakshadweep": "U06",
        "madhya pradesh": "S12",
        "maharashtra": "S13",
        "manipur": "S14",
        "meghalaya": "S15",
        "mizoram": "S16",
        "nagaland": "S17",
        "nct of delhi": "U05",
        "odisha": "S18",
        "puducherry": "U07",
        "punjab": "S19",
        "rajasthan": "S20",
        "sikkim": "S21",
        "tamil nadu": "S22",
        "telangana": "S29",
        "tripura": "S23",
        "uttar pradesh": "S24",
        "uttarakhand": "S28",
        "west bengal": "S25"
    }


def read_json(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        return data


def read_crawl_status(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        return data['CRAWL']


def read_input(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        ids = UID_MATCH.findall(data)
        print("Total IDs: %s" % len(ids))
        return ids


def easyocr(data):
    decoded_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(decoded_data))
    result = reader.readtext(image)
    return result[0][1]


class ElectoralSearchBot:
    def __init__(self, state_code):
        self.state_code = state_code
        self.result_queue = queue.Queue()
        self.WrongCaptcha = 0
        self.WrongCaptchaDecoded = 0
        self.MainTimeOut = 0
        self.Solved = 0
        self.Crashes = 0
        self.start_time = time.time()
        self.session = requests.Session()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://electoralsearch.eci.gov.in',
            'Referer': 'https://electoralsearch.eci.gov.in/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0',
            'applicationName': 'ELECTORAL_SEARCH',
            'sec-ch-ua': '"Opera";v="99", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

    def verify_captcha(self, text, captcha_id):
        url = f"https://gateway.eci.gov.in/api/v1/captcha-service/verifyCaptcha/{text}?id={captcha_id}"
        response = self.session.post(url)
        if response.status_code == 200:
            data = response.json()
            code = data['statusCode']
            return code == 200
        else:
            return False

    def single_request(self, epic_number):
        retry_chance = 10
        while True:
            time.sleep(2)
            try:
                response = self.session.get("https://gateway.eci.gov.in/api/v1/captcha-service/generateCaptcha",
                                            timeout=1)
            except Exception as e:
                self.WrongCaptcha += 1
                continue

            base64_data = response.json()["captcha"]
            captcha_id = response.json()["id"]
            captchaData = easyocr(base64_data)

            json_data = {
                "captchaData": captchaData,
                "captchaId": captcha_id,
                "epicNumber": epic_number,
                "isPortal": True,
                "securityKey": "na"
            }
            if len(self.state_code) > 0:
                json_data["stateCd"] = self.state_code

            try:
                response2 = self.session.post(
                    'https://gateway.eci.gov.in/api/v1/elastic/search-by-epic-from-national-display',
                    json=json_data, timeout=1)
            except Exception as e:
                self.MainTimeOut += 1
                continue

            if response2.status_code == 200:
                data = response2.json()
                return data

            self.WrongCaptchaDecoded += 1
            if retry_chance == 0:
                data = {"error": "retry limit exceeded"}
                return data

            retry_chance -= 1

    def filter_result(self, result, epic_number):
        d = {}
        if result and 'error' not in result[0]:
            result = result[0]['content']
            d['Epic Number'] = result['epicNumber']
            d['Name'] = result['fullName'] + '\n' + result['fullNameL1']
            d['Age'] = result['age']
            d['Relative Name'] = result['relativeFullName'] + "\n" + result['relativeFullNameL1']
            d['State'] = result['stateName']
            d['District'] = str(result['districtNo']) + "-" + result['districtValue']
            d['Assembly Constituency'] = str(result['acNumber']) + "-" + result['asmblyName']
            d['Part'] = str(result['partNumber']) + "-" + result['partName']
            d['Polling Station'] = result['psbuildingName']
            d['Part Serial Number'] = result['partSerialNumber']
        else:
            d['Epic Number'] = epic_number
        return d

    def worker(self, epic_number):
        try:
            result = self.single_request(epic_number)
            result = self.filter_result(result, epic_number)
            self.result_queue.put((epic_number, result))
            print("\n\n\n\n")
            self.Solved += 1
            print("Solved: %s" % self.Solved)
            current_time = time.time()
            time_elapsed = current_time - self.start_time
            rate = self.Solved / time_elapsed
            print("Rate: %s" % rate)
            print("Crashes: %s" % self.Crashes)
            print("TimedOUT Captcha requests: %s" % self.WrongCaptcha)
            print("Wrong Captchas: %s" % self.WrongCaptchaDecoded)
            print("Main request timeouts: %s" % self.MainTimeOut)
            print("Alive threads: %s" % threading.active_count())
        except Exception as e:
            print(e)
            self.Crashes += 1

    def process_data(self, epic_numbers):
        print("Starting...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for epic_number in epic_numbers:
                executor.submit(self.worker, epic_number)

        print("All threads finished their work.")
        end_time = time.time()
        finalData = {}
        error_data = 0
        while not self.result_queue.empty():
            epic_number, data = self.result_queue.get()
            finalData[epic_number] = data
            if not data:
                error_data += 1
        print("total error data:", error_data)
        finalData = list(finalData.values())

        total_time = end_time - self.start_time
        print("Total number of requests:", len(epic_numbers))
        print("Total time taken:", total_time, "seconds")
        print("Average request per second:", len(epic_numbers) / total_time)
        print("success rate:", self.Solved / self.WrongCaptchaDecoded)
        return finalData


def write_to_csv(data, output_file_path):
    df = pd.DataFrame(data)
    df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    run = read_crawl_status('flag.json')
    if run:
        parser = argparse.ArgumentParser()
        parser.add_argument('--input_file_path', help='Input: Input file path in text format', required=True)
        parser.add_argument('--output_file_path', help='Output: Output folder path in csv format', required=True)
        parser.add_argument('--state', help='Output: Enter state', required=False, default='')
        args = parser.parse_args()

        input_path_name = args.input_file_path
        output_folder_path = args.output_file_path
        state = args.state.strip().lower()
        states = get_states()
        ids = read_input(input_path_name)
        bot = ElectoralSearchBot(states.get(state, ''))
        data = bot.process_data(ids)
        write_to_csv(data, output_folder_path)

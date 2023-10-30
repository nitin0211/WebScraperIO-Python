import argparse
import json
import re
import os

import cv2
import numpy as np
import pdf2image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

UID_MATCH = re.compile(r"[A-Z]{2,}[A-Z\/0-9]{1,}[0-9]")


def read_json(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        return data['PDF_TO_JSON']


def solve(input_file_path, output_file_path, epic_number_output_file_name, start_page, last_page):
    pages = pdf2image.convert_from_path(str(input_file_path),
                                        first_page=start_page, last_page=last_page,
                                        dpi=300, grayscale=True)
    empty_uid = {}
    all_text = ''
    total = []
    for idx, page_3 in enumerate(pages):
        print('\nExtracting data from page {}'.format(idx + start_page))
        page_3 = np.array(page_3)
        thr = cv2.threshold(page_3, 128, 255, cv2.THRESH_BINARY_INV)[1]

        cents = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cents = cents[0] if len(cents) == 2 else cents[1]

        cents_tables = [cnt for cnt in cents if cv2.contourArea(cnt) > 10000]
        no_tables = cv2.drawContours(thr.copy(), cents_tables, -1, 0, cv2.FILLED)
        no_tables = cv2.morphologyEx(no_tables, cv2.MORPH_CLOSE, np.full((21, 51), 255))
        cents = cv2.findContours(no_tables, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cents = cents[0] if len(cents) == 2 else cents[1]
        rects = sorted([cv2.boundingRect(cnt) for cnt in cents], key=lambda r: r[1])

        rects = sorted([cv2.boundingRect(cnt) for cnt in cents_tables],
                       key=lambda r: r[1])

        for i_r, (x, y, w, h) in enumerate(rects, start=1):
            cents = cv2.findContours(page_3[y + 2:y + h - 2, x + 2:x + w - 2],
                                     cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cents = cents[0] if len(cents) == 2 else cents[1]
            inner_rects = sorted([cv2.boundingRect(cnt) for cnt in cents],
                                 key=lambda r: (r[1], r[0]))
            for (xx, yy, ww, hh) in inner_rects:
                xx += x
                yy += y
                cell = page_3[yy + 2:yy + hh - 2, xx + 2:xx + ww - 2]
                text = pytesseract.image_to_string(cell, config='--psm 6',
                                                   lang='Devanagari')
                all_text += text
                uid = UID_MATCH.findall(text)
                if not uid:
                    if not empty_uid.get('page_' + str(idx + 1), []):
                        empty_uid['page_' + str(idx + 1)] = [i_r]
                    else:
                        empty_uid['page_' + str(idx + 1)].append(i_r)
                else:
                    total.append(uid[0])

    print("Empty UID: %s" % empty_uid)
    with open(output_file_path, 'w') as f:
        f.write(all_text)

    with open(epic_number_output_file_name, 'w') as f:
        for epic in total:
            f.write(epic + '\n')


def check_positive(value):
    i_value = int(value)
    if i_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return i_value


def check_input_extension(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension != '.pdf':
        raise argparse.ArgumentTypeError(f"is an invalid file type {file_extension}, it should be .pdf")
    return file_path


def check_output_extension(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension != '.txt':
        raise argparse.ArgumentTypeError(f"is an invalid file type {file_extension}, it should be .txt")
    return file_path


def get_epic_number_output_file_name(output_file_path):
    r = output_file_path.split(".txt")[0].split("/")
    file_name, file_path = r[-1], r[:-1]
    file_path = "/".join(file_path)
    file_name = file_name + "_EpicNumber.txt"
    return f'{file_path}/{file_name}'


if __name__ == "__main__":
    run = read_json('flag.json')
    if run:
        parser = argparse.ArgumentParser()
        parser.add_argument('--input_file_path', help='Input: Input file path ,', required=True, type=check_input_extension)
        parser.add_argument('--output_file_path', help='Output: Output folder path', required=True, type=check_output_extension)
        parser.add_argument('--start_page', help='Input: Start page number', required=True, default=1,
                            type=check_positive)
        parser.add_argument('--last_page', help='Output: Last page number', required=True, default=1,
                            type=check_positive)
        args = parser.parse_args()
        input_path_name = args.input_file_path
        output_folder_path = args.output_file_path
        start_page = args.start_page
        last_page = args.last_page
        if last_page < start_page:
            raise argparse.ArgumentTypeError("Last page should be greater than start page")
        if last_page - start_page > 50:
            raise argparse.ArgumentTypeError("Last page - Start page should be less than 50 i.e. the max pages you can get is 50.")
        epic_number_output_file_name = get_epic_number_output_file_name(output_folder_path)
        solve(input_file_path=input_path_name, output_file_path=output_folder_path, epic_number_output_file_name=epic_number_output_file_name, start_page=start_page,
              last_page=last_page)

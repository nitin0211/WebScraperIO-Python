from selenium.webdriver.chrome.options import Options
from WebScraper.JsUtils import *
from WebScraper.DataExtractor import DataExtractor
from WebScraper.action.AtomAction import *
from webdriver_manager.chrome import ChromeDriverManager
from WebScraper.Utils import get_md5
from WebScraper.chrome_plugin_files.background import background_js_str
import time
import threading
import logging
import zipfile

logger = logging.getLogger(__name__)


class ChromeBrowser(object):

    _instance_lock = threading.Lock()

    def __init__(self, options, desired_capabilities, **kwargs):
        self.host, self.port = "", ""
        self.username, self.password = "", ""
        self.mainfest_json_file = 'WebScraper/chrome_plugin_files/manifest.json'
        self.options = self.chrome_options(options, desired_capabilities)
        self.rainbow = dict()
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.options)

        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(60)

        assert len(self.driver.window_handles) == 1
        self.update_urm_handle(self.driver.current_url, self.driver.current_window_handle)

    def chrome_options(self, options, desired_capabilities):
        default_options = Options()
        for option in options:
            default_options.add_argument(option)
        # plugin = self.generate_plugin()
        # default_options.add_extension(plugin)
        # emulation = {
        #     'deviceName': 'iPhone 6 Plus'
        # }
        #
        # default_options.add_experimental_option("mobileEmulation", emulation)

        # default_options.add_argument('--headless')
        default_options.add_argument('--disable-gpu')
        default_options.add_argument('--no-sandbox')
        default_options.add_argument('blink-settings=imageEnabled=false')
        default_options.add_argument('--disable-plugins')

        for key, value in desired_capabilities.items():
            default_options.capabilities[key] = value

        # Turn on the default configuration and change the pageLoadStrategy of the current web driver to eager
        # Keyword	Page load strategy state	Document readiness state(document.readyState)
        # "none"	        none	                  No correspondence
        # "eager"	        eager	                "interactive"
        # "normal"	        normal	                "complete"
        # default_options.capabilities["pageLoadStrategy"] = "eager"

        return default_options

    def quit(self):
        self.driver.close()
        self.driver.quit()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ChromeBrowser, "_instance"):
            with ChromeBrowser._instance_lock:
                if not hasattr(ChromeBrowser, "_instance"):
                    ChromeBrowser._instance = object.__new__(cls)
        return ChromeBrowser._instance

    def get_urm_handle(self, url):
        """
        Pass in the url, return to the handle maintained in the rainbow table for the url_key
        :param url:
        :return:
        """
        return self.rainbow.get(get_md5(url), None)

    def update_urm_handle(self, url, handle):
        """
        Pass in url and handle (type is str) to determine whether url_key is in the rainbow table. If yes, update, otherwise add
        :param url:
        :param handle:
        :return:
        """

        url_key = get_md5(url)

        if url_key not in self.rainbow.keys():
            self.rainbow[url_key] = handle
        else:
            url_key[url_key] = handle

    def fetch_data(self, url, sitemap, parent_selector_id):
        # Open Page
        open_action = ActionFactory.create_action("OpenAction").from_settings(url=url, in_new_tab=False).do(self)

        # Wait for the page element to load, poll the readyState of the document by default，["complete", "interactive"]
        # loading / Loading means that the document is still loading.
        # interactive / interactive, the document has been parsed, the "loading" state ends, but
        # sub-resources such as images, style sheets, and frames are still loading.
        # complete / complete, the document and all sub-resources have finished loading. The event indicating
        # the load state is about to be triggered.
        page_loaded_action = ActionFactory.create_action("WaitAction").from_settings(condition="page_loaded(None)", timeout=30).do(self, None)

        # Decoupling, waiting flexibly, avoiding using the driver.page_source attribute to get the html elements of the
        # webpage
        time.sleep(10)
        parent_element = self.driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")

        dataExtractor = DataExtractor(self, url, sitemap, parent_selector_id, parent_element)
        results = dataExtractor.get_data()

        return results

    def generate_plugin(self):
        manifest_json, background_js = self.get_plugin_file_data()
        pluginfile = self.generate_plugin_file_name()
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return pluginfile

    def generate_plugin_file_name(self):
        return "proxy_auth_plugin.zip"

    def get_plugin_file_data(self):
        manifest_json = self.read_from_text_file(self.mainfest_json_file)
        background_js = background_js_str % (self.host, self.port, self.username, self.password)
        return manifest_json, background_js

    def read_from_text_file(self, filename):
        with open(filename) as file:
            text = file.read()
        return text

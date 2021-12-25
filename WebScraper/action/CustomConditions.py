from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from WebScraper.JsUtils import DOCUMENT_STATUS, JQUERY_AJAX_STATUS
import re

class page_loaded(object):
    def __init__(self, re_exp):
        """
        Judge according to the incoming re_exp, if it is None or an empty string, assign the default value to the state
        array ["complete", "interactive"]
        :param re_exp:
        """
        if not re_exp or re_exp == "":
            self.re_exp = ["complete", "interactive"]
        else:
            self.re_exp = re_exp

    def __call__(self, driver, *args, **kwargs):
        status = driver.execute_script(DOCUMENT_STATUS)
        # print("Wait for page load completed, current status is --> {}".format(status))
        return True if status in self.re_exp else False


class ajax_loaded_complete(object):
    """At this stage, only ajax waiting implemented with jquery is supported"""
    def __init__(self, type):
        """
        The implementation method of incoming ajax request, such as jQuery, AngularJS, etc.
        :param type:
        """
        # TODO Ajax request type, which needs to be supplemented later
        self.type = type

    def __call__(self, driver, *args, **kwargs):
        if self.type == "jQuery":
            status = driver.execute_script(JQUERY_AJAX_STATUS)
            # print("Wait for ajax response completed, current status is --> {}".format(status))
            return True if status else False
        else:
            return True
from . import Selector, RegisterSelectorType
from WebScraper.action import ActionFactory
from WebScraper.Utils import setInterval
from WebScraper.UniqueElementList import UniqueElementList
from selenium.webdriver.common.by import By
import time


@RegisterSelectorType("SelectorElementClick")
class ClickSelector(Selector):
    features = {
        "multiple": False,
        "delay": 0,
        "clickElementSelector": "",
        "clickType": "",
        "discardInitialElements": "",
        "clickElementUniquenessType": ""
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, **kwargs):
        super(ClickSelector, self).__init__(id, type, selector, parentSelectors)
        self.multiple = multiple
        self.delay = 0 if delay == "" else delay
        self.actions = ActionFactory.create_action("ClickAction").from_settings(**kwargs)

    @classmethod
    def get_features(cls):
        base_features = Selector.get_features()
        base_features.update(cls.features)
        return base_features

    def will_return_multiple_records(self):
        return self.can_return_multiple_records() and self.multiple

    def can_return_multiple_records(self):
        return True

    def can_have_child_selectors(self):
        return True

    def can_have_local_child_selectors(self):
        return True

    def can_create_new_jobs(self):
        return False

    def will_return_elements(self):
        return True

    # def get_click_elements(self, driver, job_url, parentElement):
    #     click_css_path = self.actions.protocol.get("click_path")
    #
    # def get_item_css_path(self, driver, element):
    #     return driver.execute_script(GET_ITEM_CSS_PATH, element)
    #
    #
    # def trigger_element_click(self):
    #     pass
    #
    #

    def get_specific_data(self, browser, job_url, parent_element):
        driver = browser.driver

        found_elements = UniqueElementList("unique_html_text")

        self.actions.get_click_elements(driver, job_url)

        initial_elements = self.get_data_elements(driver, job_url, parent_element)

        for element in initial_elements:
            found_elements.push(element)

        if self.actions.protocol.get("discardInitialElements") == "discard":
            found_elements = UniqueElementList("unique_text")

        if len(self.actions.waiting_elements) == 0:
            return found_elements

        time_step = float(self.delay)

        next_click_time = time.time()

        def click_func(stop_event, *args, **kwargs):
            nonlocal time_step
            nonlocal next_click_time

            now = time.time()

            if now < next_click_time:
                return

            # Click on
            self.actions.do(browser, job_url)

            parent_elements = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
            data_elements = self.get_data_elements(driver, job_url, parent_elements)

            add_some_element = False
            for item in data_elements:
                added = found_elements.push(item)
                if added:
                    add_some_element = True

            if len(self.actions.waiting_elements) == 0:
                stop_event.set()
            else:
                next_click_time = now + time_step

        inter = setInterval(1, click_func)

        return found_elements

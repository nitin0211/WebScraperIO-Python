
from . import RegisterSelectorType, Selector
from WebScraper.Utils import setInterval
from selenium.webdriver.common.by import By
from WebScraper.action import ActionFactory

import time


@RegisterSelectorType("SelectorElementScroll")
class ScrollSelector(Selector):

    can_return_multiple_records = True
    can_have_child_selectors = True
    can_have_local_child_selectors = True
    can_create_new_jobs = False
    can_return_elements = True

    features = {
        "multiple": False,
        "delay": 0,
        "scroll_type": "N"
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, scroll_type, **kwargs):
        super(ScrollSelector, self).__init__(id, type, selector, parentSelectors)
        self.multiple = multiple
        self.delay = 0 if delay == "" else delay
        self.action = ActionFactory.create_action("ScrollAction").from_settings(scroll_type)

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

    def get_specific_data(self, browser, job_url, parent_element):
        driver = browser.driver

        found_elements = self.get_data_elements(driver, job_url, parent_element)
        pre_len = len(found_elements)

        time_step = float(self.delay)
        next_scroll_time = time.time()

        def scroll_func(stop_event, *args, **kwargs):
            nonlocal found_elements
            nonlocal next_scroll_time
            nonlocal time_step
            nonlocal pre_len

            now = time.time()

            if now < next_scroll_time:
                return

            # Scroll
            scroll_percent = self.action.do(browser, job_url)
            parent_elements = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
            found_elements = self.get_data_elements(driver, job_url, parent_elements)
            cur_len = len(found_elements)
            # print(cur_len, pre_len, scroll_percent)
            if cur_len > pre_len or scroll_percent < 100:
                pre_len = cur_len
                next_scroll_time = now + time_step
            else:
                stop_event.set()

        setInterval(15, scroll_func)
        return found_elements

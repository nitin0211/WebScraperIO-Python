
from . import RegisterSelectorType, Selector
from WebScraper.Utils import setInterval
from selenium.webdriver.common.by import By
from WebScraper.action import ActionFactory
from WebScraper.selector import ElementQuery
import time
from WebScraper.UniqueElementList import UniqueElementList


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
        "scrollElementSelector": ""
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, **kwargs):
        super(ScrollSelector, self).__init__(id, type, selector, parentSelectors)
        self.multiple = multiple
        self.delay = 0 if delay == "" else delay
        self.action = ActionFactory.create_action("ScrollAction").from_settings(**kwargs)

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

    def scroll(self, browser, parent_element):
        if self.action.protocol.get("scrollElementSelector"):
            scroll_elements = ElementQuery(self.action.protocol.get("scrollElementSelector"), parent_element).execute()
            if scroll_elements:
                browser.driver.execute_script('arguments[0].scrollIntoView(true);', scroll_elements[0])
        else:
            browser.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    # def get_specific_data(self, browser, job_url, parent_element):
    #     driver = browser.driver
    #
    #     found_elements = self.get_data_elements(driver, job_url, parent_element)
    #     pre_len = len(found_elements)
    #
    #     time_step = float(self.delay)
    #     next_scroll_time = time.time()
    #
    #     def scroll_func(stop_event, *args, **kwargs):
    #         nonlocal found_elements
    #         nonlocal next_scroll_time
    #         nonlocal time_step
    #         nonlocal pre_len
    #
    #         now = time.time()
    #
    #         if now < next_scroll_time:
    #             return
    #
    #         # Scroll
    #         scroll_percent = self.action.do(browser, job_url)
    #         parent_elements = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
    #         found_elements = self.get_data_elements(driver, job_url, parent_elements)
    #         cur_len = len(found_elements)
    #         # print(cur_len, pre_len, scroll_percent)
    #         if cur_len > pre_len or scroll_percent < 100:
    #             pre_len = cur_len
    #             next_scroll_time = now + time_step
    #         else:
    #             stop_event.set()
    #
    #     setInterval(15, scroll_func)
    #     return found_elements

    def get_specific_data(self, browser, job_url, parent_element):
        driver = browser.driver

        found_elements = UniqueElementList("uniqueHTMLText")

        elements = self.get_data_elements(driver, job_url, parent_element)
        # pre_len = len(found_elements)
        for element in elements:
            found_elements.push(element)

        self.scroll(browser, parent_element)
        time_step = float(self.delay)
        next_scroll_time = time.time() + time_step

        def scroll_func(stop_event, *args, **kwargs):
            # nonlocal found_elements
            nonlocal next_scroll_time
            nonlocal time_step
            # nonlocal pre_len

            now = time.time()

            if now < next_scroll_time:
                return

            parent_element = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
            elements_ = self.get_data_elements(browser, job_url, parent_element)
            added_an_element = False
            for item in elements_:
                added = found_elements.push(item)
                if added:
                    added_an_element = True
            # Scroll
            if not added_an_element:
                stop_event.set()
            else:
                self.scroll(browser, parent_element)
                next_scroll_time = now + time_step

        setInterval(1, scroll_func)
        return found_elements

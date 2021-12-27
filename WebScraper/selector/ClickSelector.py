from . import Selector, RegisterSelectorType
from WebScraper.action import ActionFactory
from WebScraper.Utils import setInterval
from WebScraper.UniqueElementList import UniqueElementList
from selenium.webdriver.common.by import By
import time
from WebScraper.JsUtils import TRIGGER_ELEMENT_CLICK, GET_ITEM_CSS_PATH
from WebScraper.selector import ElementQuery


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

    def get_click_elements(self, parent_element):
        click_elements = ElementQuery(self.actions.protocol.get("clickElementSelector"), parent_element).execute()
        return click_elements

    def trigger_button_click(self, browser, click_element):
        # css_selector = browser.driver.execute_script(GET_ITEM_CSS_PATH, click_element)
        # print(css_selector)
        browser.driver.execute_async_script(TRIGGER_ELEMENT_CLICK, click_element)

    def get_specific_data(self, browser, job_url, parent_element):
        driver = browser.driver

        found_elements = UniqueElementList("uniqueHTMLText")

        elements = self.get_data_elements(driver, job_url, parent_element)
        if self.actions.protocol.get("discardInitialElements") == "don-not-discard":
            for element in elements:
                found_elements.push(element)

        click_elements = self.actions.get_click_elements(browser, job_url)
        if len(click_elements) == 0:
            return found_elements

        done_clicking_elements = UniqueElementList(self.actions.protocol.get("clickElementUniquenessType", "uniqueText"))

        current_click_element = click_elements[0]
        if self.actions.protocol.get('clickType') == 'clickOnce':
            done_clicking_elements.push(current_click_element)
        self.trigger_button_click(browser, current_click_element)

        time_step = float(self.delay)
        next_element_selection = time.time() + time_step

        def click_func(stop_event, *args, **kwargs):
            # nonlocal time_step
            nonlocal next_element_selection
            nonlocal current_click_element
            nonlocal click_elements

            now = time.time()
            if now < next_element_selection:
                print("inside return")
                return

            parent_element = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
            elements_ = self.get_data_elements(browser, job_url, parent_element)
            added_an_element = False
            for item in elements_:
                added = found_elements.push(item)
                if added:
                    added_an_element = True
            if not added_an_element:
                done_clicking_elements.push(current_click_element)

            click_elements = self.actions.get_click_elements(browser, job_url)

            click_elements = list(filter(lambda x: not done_clicking_elements.is_added(x), click_elements))

            if len(click_elements) == 0:
                stop_event.set()
            else:
                current_click_element = click_elements[0]
                if self.actions.protocol.get("clickType") == 'clickOnce':
                    done_clicking_elements.push(current_click_element)
                self.trigger_button_click(browser, current_click_element)
                next_element_selection = now + time_step

        inter = setInterval(1, click_func)
        return found_elements


from . import RegisterActionType, Action, ActionFactory

from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from WebScraper.JsUtils import WINDOW_OPEN
from WebScraper.action.CustomConditions import *
from WebScraper.JsUtils import TRIGGER_ELEMENT_CLICK, GET_ITEM_CSS_PATH, SCROLL_TO_BOTTOM

import logging

logger = logging.getLogger(__name__)


@RegisterActionType("OpenAction")
class OpenAction(Action):

    def __init__(self, protocol):
        super(OpenAction, self).__init__(protocol=protocol)

    def pre_check(self, protocol):
        pass

    def do(self, browser, *args, **kwargs):
        driver = browser.driver
        url = self.protocol.get("url", None)
        in_new_tab = self.protocol.get("in_new_tab", False)

        try:
            logger.info("OpenAction start to load url -> {}, with open type -> {}".format(url, in_new_tab))
            cur_handle_num = len(driver.window_handles)

            driver_current_url = driver.current_url
            if driver_current_url == "data:,":
                driver.execute_script(WINDOW_OPEN.format(url, '_self'))
                assert len(driver.window_handles) == 1
                return

            if in_new_tab:
                driver.execute_script(WINDOW_OPEN.format(url, '_blank'))
                assert len(driver.window_handles) - cur_handle_num == 1

            else:
                driver.execute_script(WINDOW_OPEN.format(url, '_self'))
                assert len(driver.window_handles) - cur_handle_num == 0

        except TimeoutError as e:
            logger.info("Selenium failed to open the url, caused by:{}".format(e))

            browser.quit()

    @classmethod
    def from_settings(cls, url, in_new_tab):
        return cls({"url": url, "in_new_tab": in_new_tab})


@RegisterActionType("WaitAction")
class WaitAction(Action):
    """
    {"condition":"", "timeout": 5}
    """
    MAX_WAIT_TIME = 60

    def __init__(self, protocol):
        super(WaitAction, self).__init__(protocol=protocol)

    def pre_check(self, protocol):
        condition = protocol.get("condition", None)
        timeout = protocol.get("timeout", 0)

        if isinstance(condition, (str, bytes)):
            if condition: condition = eval(condition)
        elif not isinstance(condition, int) or callable(condition):
            pass
        protocol["condition"] = condition
        protocol["timeout"] = self.MAX_WAIT_TIME if timeout > self.MAX_WAIT_TIME else timeout

    def do(self, browser, url, *args, **kwargs):
        driver = browser.driver

        condition = self.protocol.get("condition")
        timeout = self.protocol.get("timeout")

        if callable(condition):
            WebDriverWait(driver, timeout).until(condition)
        elif isinstance(condition, int):
            pass
        else:
            WebDriverWait(driver, timeout).until(lambda _: False)

    @classmethod
    def from_settings(cls, condition, timeout):
        return cls({"condition": condition, "timeout": timeout})


@RegisterActionType("ClickAction")
class ClickAction(Action):
    """
        {"click_path":"div.a"}
    """
    def __init__(self, protocol):
        super(ClickAction, self).__init__(protocol=protocol)

    def pre_check(self, protocol):
        pass

    def get_click_elements(self, driver, url, *args, **kwargs):
        """
        :param driver:
        :param url:
        :param args:
        :param kwargs:
        :return:
        """
        result_css_path = list()

        click_path = self.protocol.get("clickElementSelector")
        click_elements = driver.find_elements(By.CSS_SELECTOR, click_path)

        for single_click_element in click_elements:
            cur_path = driver.execute_script(GET_ITEM_CSS_PATH, single_click_element)
            result_css_path.append(cur_path)

        if not hasattr(self, "waiting_elements"):
            self.__setattr__("waiting_elements", result_css_path)

    def do(self, browser, url, *args, **kwargs):
        driver = browser.driver

        if not hasattr(self, "waiting_elements"):
            raise AttributeError

        orgin_handles = len(driver.window_handles)

        current_click_element = self.waiting_elements.pop(0)

        driver.execute_async_script(TRIGGER_ELEMENT_CLICK, current_click_element)

        assert len(driver.window_handles) == orgin_handles

    @classmethod
    def from_settings(cls, clickElementSelector, clickElementUniquenessType, clickType, discardInitialElements):
        return cls({"clickElementSelector": clickElementSelector, "clickElementUniquenessType": clickElementUniquenessType, "clickType": clickType, "discardInitialElements": discardInitialElements})


@RegisterActionType("ScrollAction")
class ScrollAction(Action):
    """
        {"scroll_type":"N/integer"}
    """
    def __init__(self, protocol):
        super(ScrollAction, self).__init__(protocol=protocol)

    def pre_check(self, protocol):
        pass

    def do(self, browser, url,  **kwargs):
        driver = browser.driver

        scroll_percent = 0
        scroll_percent = driver.execute_async_script(SCROLL_TO_BOTTOM)

        return scroll_percent

    @classmethod
    def from_settings(cls, scroll_type):
        return cls({"scroll_type": scroll_type})


@RegisterActionType("CloseAction")
class CloseAction(Action):

    def __init__(self, protocol):
        super(CloseAction, self).__init__(protocol=protocol)

    def pre_check(self, protocol):
        pass

    def do(self, browser, url, **kwargs):
        driver = browser.driver
        self.driver.close()
        self.driver.quit()

    @classmethod
    def from_settings(cls, dummy):
        return cls({"dummy": dummy})



from . import RegisterSelectorType, Selector
from pyquery import PyQuery as pq

from WebScraper.processor import ProcessorFactory


@RegisterSelectorType("SelectorText")
class TextSelector(Selector):

    features = {
        "multiple": False,
        "delay": 0,
        "regex": str()
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, regex, **kwargs):
        super(TextSelector, self).__init__(id, type, selector, parentSelectors)

        self.multiple = multiple
        self.delay = delay
        self.regex = regex

        if self.regex and self.regex != "":
            self.regex_processor = ProcessorFactory.create_processor("RegexProcessor").from_settings(self.regex)

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
        return False

    def can_have_local_child_selectors(self):
        return False

    def can_create_new_jobs(self):
        return False

    def will_return_elements(self):
        return False

    def get_specific_data(self, driver, job_url, parent_element):
        elements = self.get_data_elements(driver, job_url, parent_element)

        resultData = list()

        for element in elements:
            data = dict()
            text = pq(element).text()
            if hasattr(self, "regex_processor"):
                text = self.regex_processor(text)

            data[self.id] = text

            resultData.append(data)

        if not self.multiple and len(elements) == 0:
            data = dict()
            data[self.id] = None
            resultData.append(data)

        return resultData


from . import RegisterSelectorType, Selector


@RegisterSelectorType("SelectorElement")
class ElementSelector(Selector):

    features = {
        "multiple": False,
        "delay": 0
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, **kwargs):
        super(ElementSelector, self).__init__(id, type, selector, parentSelectors)
        self.multiple = multiple
        self.delay = delay

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

    def get_specific_data(self, driver, job_url, parent_element):
        elements = self.get_data_elements(driver, job_url, parent_element)
        return list(elements)


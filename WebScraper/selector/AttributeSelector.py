from . import Selector, RegisterSelectorType
from pyquery import PyQuery as pq


@RegisterSelectorType("SelectorElementAttribute")
class AttributeSelector(Selector):

    features = {
        "multiple": False,
        "delay": 0,
        "extractAttribute": ""
    }

    def __init__(self, id, type, selector, parentSelectors, multiple, delay, extractAttribute, **kwargs):
        super(AttributeSelector, self).__init__(id, type, selector, parentSelectors)
        self.multiple = multiple
        self.delay = delay
        self.extract_attribute = extractAttribute

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
        resultData = list()
        elements = self.get_data_elements(driver, job_url, parent_element)

        if not self.multiple and len(elements) == 0:
            data = dict()
            data[self.id] = None
            resultData.append(data)

            return resultData

        for element in elements:
            pq_object = pq(element)
            data = dict()

            if self.will_return_new_jobs():
                data[self.id] = pq_object.attr(self.extract_attribute)
                data["_followSelectorId"] = self.id
                data[str(self.id) + "-href"] = pq_object.attr(self.extract_attribute)
                data["_follow"] = pq_object.attr(self.extract_attribute)

                resultData.append(data)

            else:
                data[self.id] = pq_object.attr(self.extract_attribute)
                resultData.append(data)

        return resultData

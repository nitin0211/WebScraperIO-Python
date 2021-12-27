from pyquery import PyQuery as pq


class RegisterSelectorType(object):

    selector_type = {}

    def __init__(self, type):
        self._type = type

    def __call__(self, cls, *args, **kwargs):
        if not self.selector_type.__contains__(self._type):
            self.selector_type[self._type] = cls
        return cls


class Selector(object):
    can_return_multiple_records = False
    can_have_child_selectors = False
    can_have_local_child_selectors = False
    can_create_new_jobs = False
    can_return_elements = False

    features = {
        'id': '',
        'type': None,
        'selector': '',
        'parentSelectors': []
    }

    @classmethod
    def get_features(cls):
        return cls.features.copy()

    @classmethod
    def from_settings(cls, settings):
        
        features = cls.get_features()

        for key in list(settings.keys()):
            if key not in features.keys():
                del settings[key]

        for key, value in features.items():
            if key not in settings.keys():
                settings[key] = value
        selector = cls(**settings)

        return selector

    def __init__(self, id, type, selector, parentSelectors, **kwargs):
        """
        :param id:
        :param type:
        :param selector:
        :param parentSelectors:
        :param kwargs:
        """
        self.id = id
        self.type = type
        self.selector = selector
        self.parentSelectors = parentSelectors
        # self.children = []

    def will_return_multiple_records(self):
        raise NotImplementedError()

    def will_return_elements(self):
        raise NotImplementedError()

    def get_data(self, browser, job_url, parent_element):
        """
        :param browser:
        :param job_url:
        :param parent_element:
        :return:
        """

        return self.get_specific_data(browser, job_url, parent_element)

    def get_data_elements(self, browser, url, parent_element):
        elements = ElementQuery(self.selector, parent_element).execute()

        if self.will_return_multiple_records():
            return elements
        else:
            return elements[:1] if elements else []

    def get_specific_data(self, driver, job_url, parent_element):
        raise NotImplementedError()

    def has_parent_selector(self, selector_id):
        return selector_id in self.parentSelectors


class ElementQuery(object):

    def __init__(self, cssselector, parent_element):
        self.cssselector = cssselector if cssselector else ""
        self.parentElement = parent_element
        self.selectedElements = list()

    def add_element(self, element):
        if element not in self.selectedElements:
            self.selectedElements.append(element)

    def get_selector_parts(self):
        resultSelectors = []
        currentSelector = ""

        regEx = r"(,|\".*?\"|\'.*?\'|\(.*?\))"
        cssPaths = self.cssselector.split(regEx)
        for css in cssPaths:
            if css == ",":
                if currentSelector.strip().__len__() > 0:
                    resultSelectors.append(currentSelector)
                else:
                    currentSelector = ""
            else:
                currentSelector += css
        if currentSelector.strip().__len__() > 0:
            resultSelectors.append(currentSelector)

        return resultSelectors

    def execute(self):
        selectorParts = self.get_selector_parts()
        for selector in selectorParts:
            elements = pq(self.parentElement)(selector)
            for item in elements:
                self.add_element(item)
        return self.selectedElements

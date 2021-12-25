import re

class Job(object):

    def __init__(self, url, parentSelectorId, scraper, parentJob, baseData):
        if parentJob:
            self.url = self.process_url(parentJob.url, url)
        else:
            self.url = url

        self.parentSelectorId = parentSelectorId
        self.scraper = scraper
        self.dataItems = list()
        self.baseData = baseData if baseData else dict()

    def process_url(self, parent_url, child_url):

        regex = re.compile(r"(https?://)?([a-z0-9\-.]+\.[a-z0-9\-]+(:\d+)?|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?)?(/[^?]*/|/)?([^?]*)?(\?.*)?")

        parent_group = list(regex.match(parent_url).groups())
        child_group = list(regex.match(child_url).groups())

        abso_url = str()

        if not child_group[0] and not child_group[1] and not child_group[4] and not child_group[5]:
            abso_url += parent_group[0] + parent_group[1] + parent_group[4] + parent_group[5] + child_group[6]
            return abso_url

        if not child_group[0]:
            child_group[0] = parent_group[0]

        if not child_group[1]:
            child_group[1] = parent_group[1]

        if not child_group[4]:
            if not parent_group[4]:
                child_group[4] = "/"
            else:
                child_group[4] = parent_group[4]

        if not child_group[5]:
            child_group[5] = ""
        if not child_group[6]:
            child_group[6] = ""

        abso_url += child_group[0] + child_group[1] + child_group[4] + child_group[5] + child_group[6]

        return abso_url

    def execute(self, browser):
        sitemap = self.scraper.sitemap
        results = browser.fetch_data(self.url, sitemap, self.parentSelectorId)

        # TODO results，dataItems

        for item in results:
            for key in self.baseData.keys():
                if key not in item.keys():
                    item[key] = self.baseData.get(key)

            self.dataItems.append(item)

    def get_results(self):
        return self.dataItems

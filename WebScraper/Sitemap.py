from WebScraper.selector.TextSelector import TextSelector
from WebScraper.selector.LinkSelector import LinkSelector
from WebScraper.selector.ElementSelector import ElementSelector
from WebScraper.selector.ScrollSelector import ScrollSelector
from WebScraper.selector.ClickSelector import ClickSelector
from WebScraper.selector.AttributeSelector import AttributeSelector
from WebScraper.SelectorList import SelectorList

import logging
import json

logger = logging.getLogger(__name__)


class Sitemap(object):

    def __init__(self, id, startUrl, selectorsStr):
        self.id = id
        self.startUrl = startUrl
        self.selectors = SelectorList(selectorsStr)
        List = json.dumps(self.selectors, default=lambda o: o.__dict__)

    def get_all_selectors(self, parent_selector):
        return self.selectors.get_all_selectors(parent_selector)

    def get_direct_child_selectors(self, parent_selector):
        return self.selectors.get_direct_child_selectors(parent_selector)

    def get_selector_by_id(self, selector_id):
        return self.selectors.get_selector_by_id(selector_id)

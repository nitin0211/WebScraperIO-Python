
from pyquery import PyQuery as pq
from WebScraper.Utils import get_md5
from lxml.etree import _ElementUnicodeResult


class UniquenessTypeNotImplementedError(Exception):
    pass


class UniqueElementList(list):

    def __init__(self, uniqueness_type):
        super(UniqueElementList, self).__init__()

        self.uniqueness_type = uniqueness_type
        self.existed_elements = dict()

    def get_uniqueness_id(self, parent_element):
        if self.uniqueness_type == "uniqueText":
            pq_object = pq(parent_element)
            text = pq_object.text()
            # element_id = get_md5(text)

            return text

        elif self.uniqueness_type == "uniqueHTMLText":
            pq_object = pq(parent_element)

            element_html = pq("<div class='-scraper-element-wrapper'></div>").append(pq_object.eq(0).clone()).html()

            element_id = get_md5(element_html)

            return element_id

        elif self.uniqueness_type == "uniqueHTML":
            pq_object = pq(parent_element)

            if pq_object[0].text:
                pq_object[0].text = None
            if pq_object[0].tail:
                pq_object[0].tail = None

            def _recursive_del_text(pq_object):
                element_node_lists = pq_object.contents().filter(lambda i, this: not isinstance(this, _ElementUnicodeResult))
                # Assigning None maybe a bug
                for node in element_node_lists:
                    if node.tail:
                        node.tail = None
                    if node.text:
                        node.text = None

                    _recursive_del_text(pq(node))

                return element_node_lists

            _recursive_del_text(pq_object)
            element_html = pq("<div class='-scraper-element-wrapper'></div>").append(pq_object).html()
            element_id = get_md5(element_html)

            return element_id

        elif self.uniqueness_type == "uniqueCSSSelector":
            pass
        else:
            raise UniquenessTypeNotImplementedError()

    def push(self, parent_element):
        if self.is_added(parent_element):
            return False
        else:
            element_uniqueness_id = self.get_uniqueness_id(parent_element)
            self.existed_elements[element_uniqueness_id] = True
            self.append(parent_element)
            return True

    def is_added(self, parent_element):
        element_uniqueness_id = self.get_uniqueness_id(parent_element)
        return self.existed_elements.get(element_uniqueness_id, False)

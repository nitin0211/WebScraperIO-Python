from collections.abc import MutableSequence
from WebScraper.selector import RegisterSelectorType
from WebScraper.selector import Selector


class SelectorList(MutableSequence):
    __selector_type = RegisterSelectorType.selector_type

    @classmethod
    def create_selector(cls, selector_type):
        if cls.__selector_type.__contains__(selector_type):
            return cls.__selector_type[selector_type]
        else:
            raise NotImplementedError()

    def __init__(self, selectors=None):
        super(SelectorList, self).__init__()
        self._list = list()
        for i in range(len(selectors or [])):
            self.append(selectors[i])

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __delitem__(self, ii):
        """Delete an item"""
        del self._list[ii]

    def __setitem__(self, ii, selector):
        # optional: self._acl_check(val)
        self._list[ii] = selector

    def __str__(self):
        return str(self._list)

    def insert(self, ii, selector):
        # optional: self._acl_check(val)
        self._list.insert(ii, selector)

    def extend(self, other):
        if isinstance(other, SelectorList):
            self._list.extend(other._list)
        else:
            self._list.extend(other)

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["_list"] = self.__dict__["_list"][:]
        return inst

    def copy(self):
        return self.__class__(self)

    def append(self, selector):
        if isinstance(selector, Selector):
            selector_id = selector.id
        else:
            selector_id = selector.get("id")
        if not self.has_selector(selector_id):
            if not isinstance(selector, Selector):
                child_selector_class = SelectorList.create_selector(selector.get("type"))
                selector = child_selector_class.from_settings(selector)
            self.insert(len(self._list), selector)

    def has_selector(self, selector_id) -> bool:
        for i in range(len(self._list)):
            if self._list[i].id == selector_id:
                return True
        return False

    def get_selector_by_id(self, selector_id):
        for i in range(len(self._list)):
            selector = self._list[i]
            if selector.id == selector_id:
                return selector
        return None

    def get_all_selectors(self, parent_selector_id):
        if not parent_selector_id:
            return self

        child_selectors = []

        def get_all_child_selectors(parent_selectorid, result_selectors):
            for selector in self._list:
                if selector.has_parent_selector(parent_selectorid):
                    if selector.id not in result_selectors:
                        result_selectors.append(selector.id)
                        child_selectors.append(selector)
                        get_all_child_selectors(selector.id, result_selectors)

        get_all_child_selectors(parent_selector_id, list())
        return child_selectors

    def get_direct_child_selectors(self, parent_selector):
        result_selectors = SelectorList()
        for selector in self._list:
            if selector.has_parent_selector(parent_selector):
                result_selectors.append(selector)
        return result_selectors

    def will_return_multiple_records(self, selector_id):
        selector = self.get_selector_by_id(selector_id)
        if selector.will_return_multiple_records():
            return True

        child_selectors = self.get_all_selectors(selector_id)
        for selector in child_selectors:
            if selector.will_return_multiple_records():
                return True
        return False

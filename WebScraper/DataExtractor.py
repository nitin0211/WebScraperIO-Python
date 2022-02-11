from WebScraper.SelectorList import SelectorList


class DataExtractor(object):

    def __init__(self, browser, url, sitemap, parentSelectorId, parentElement, *args, **kwargs):
        self.url = url
        self.browser = browser
        self.sitemap = sitemap
        self.parentSelectorId = parentSelectorId
        self.parentElement = parentElement

    def get_data(self):
        data_result = list()

        selectorTrees = self.find_selector_trees()
        for oneSelectorTree in selectorTrees:
            results = self.get_selector_tree_data(oneSelectorTree, self.parentSelectorId, self.parentElement, {})
            data_result.extend(results)

        return data_result

    def find_selector_trees(self):
        return self._find_selector_trees(self.parentSelectorId, SelectorList())

    def selector_is_common_to_all_trees(self, selector):
        if selector.will_return_multiple_records():
            return False
        if selector.can_create_new_jobs() and self.sitemap.get_direct_child_selectors(selector.id):
            return False
        child_selectors = self.sitemap.get_all_selectors(selector.id)
        for child in child_selectors:
            if not self.selector_is_common_to_all_trees(child):
                return False
        return True

    def get_selectors_common_to_all_trees(self, parent_selector_id):
        common_selectors = list()
        child_selectors = self.sitemap.get_direct_child_selectors(parent_selector_id)
        for child_selector in child_selectors:
            if self.selector_is_common_to_all_trees(child_selector):
                common_selectors.append(child_selector)
                selector_child_selectors = self.sitemap.get_all_selectors(child_selector.id)
                for selector in selector_child_selectors:
                    if selector not in common_selectors:
                        common_selectors.append(selector)
        return common_selectors

    def _find_selector_trees(self, parent_selector_id, common_selectors_from_parent):
        common_selectors = common_selectors_from_parent.copy()
        common_selectors.extend(self.get_selectors_common_to_all_trees(parent_selector_id))
        selector_trees = []
        child_selectors = self.sitemap.get_direct_child_selectors(parent_selector_id)
        for selector in child_selectors:
            if not self.selector_is_common_to_all_trees(selector):
                if not selector.can_have_local_child_selectors():
                    selector_tree = common_selectors.copy()
                    selector_tree.append(selector)
                    selector_trees.append(selector_tree)
                else:
                    common_selectors_from_parent = common_selectors.copy()
                    common_selectors_from_parent.append(selector)
                    child_selector_trees = self._find_selector_trees(selector.id, common_selectors_from_parent)
                    selector_trees.extend(child_selector_trees)
        if len(selector_trees) == 0:
            selector_trees.append(common_selectors)
        return selector_trees

    def get_selector_tree_common_data(self, selectors, parent_selector_id, parent_element):
        common_data = {}
        child_selectors = selectors.get_direct_child_selectors(parent_selector_id)
        for selector in child_selectors:
            if not selectors.will_return_multiple_records(selector.id):
                current_common_data = self.get_selector_common_data(selectors, selector, parent_element)
                common_data.update(current_common_data)
        return common_data

    def get_selector_common_data(self, selectors, selector, parent_element):
        data = selector.get_data(self.browser, self.url, parent_element)
        if not data:
            return data
        if selector.will_return_elements():
            new_parent_element = data[0]
            data = self.get_selector_tree_common_data(selectors, selector.id, new_parent_element)
            return data
        return data[0]

    def get_multi_selector_data(self, selectors, selector, parent_element, common_data):
        result_data = []
        if not selector.will_return_elements():
            selector_data = selector.get_data(self.browser, self.url, parent_element)
            new_common_data = common_data.copy()
            for record in selector_data:
                record.update(new_common_data)
                result_data.append(record)
            return result_data

        selector_data = selector.get_data(self.browser, self.url, parent_element)
        for element in selector_data:
            new_common_data = common_data.copy()
            child_records = self.get_selector_tree_data(selectors, selector.id, element, new_common_data)
            for record in child_records:
                record.update(new_common_data)
                result_data.append(record)
        return result_data

    def get_selector_tree_data(self, selectors, parent_selector_id, parent_element, common_data):
        result_data = []
        child_selectors = selectors.get_direct_child_selectors(parent_selector_id)
        child_common_data = self.get_selector_tree_common_data(selectors, parent_selector_id, parent_element)
        common_data.update(child_common_data)
        for selector in child_selectors:
            if selectors.will_return_multiple_records(selector.id):
                new_common_data = common_data.copy()
                responses = self.get_multi_selector_data(selectors, selector, parent_element, new_common_data)
                for child_record in responses:
                    rec = {}
                    rec.update(child_record)
                    result_data.append(rec)
        if len(result_data) == 0:
            if len(common_data.keys()) == 0:
                return []
            else:
                result_data.append(common_data)
                return result_data
        else:
            return result_data

from crawl_helpers import FilterListBySuffix
import unittest

class FilterListBySuffixTest(unittest.TestCase):
    def setUp(self):
        self.items = ['string1.suffix1',
                      'string2.suffix1',
                      'string3.suffix2',
                      'string4.suffix3']
        
    def testFilterListBySuffixWorks(self):
        new_list = FilterListBySuffix(self.items, '.suffix1')
        assert len(new_list) == 2
        assert new_list[0] == 'string1.suffix1'
        assert new_list[1] == 'string2.suffix1'

if __name__ == "__main__":
    unittest.main()


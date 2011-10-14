from google_helper import GoogleSearch
import unittest

class GoogleSearchTest(unittest.TestCase):
    def testGoogleSearchWorks(self):
        # Attention: this test is flaky for a set of reasons: the number of
        # requests per day is limited, and the first 10 results for Google
        # might not contain 'http://www.google.com' (but this is less probable).
        search_results = GoogleSearch('AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                                      '017513622067795982245:_iwk5xznrk0',
                                      'Google')
        assert len(filter(lambda r: r.url == 'http://www.google.com/',
                          search_results)) > 0

from scraper import ScraperBase

import re

class IvPasteHelper(ScraperBase):

    TEST_URL = 'http://ivpaste.com/v/8Gq82p8y'
    TEST_RESULTS = ['http://news.ycombinator.com']

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://ivpaste.com')

    def expand(self, url, **extra):
        soup = self.get_soup(url.replace("/v/","/p/"), headers={'Referer':url})

        links = soup.select('table a')
        links = [link['href'] for link in links]

        return links

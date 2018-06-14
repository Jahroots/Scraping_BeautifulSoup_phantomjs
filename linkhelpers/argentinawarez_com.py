from sandcrawler.scraper import ScraperBase


class ArgentinaWarezHelper(ScraperBase):

    TEST_URL = "http://www.argentinawarez.com/link/?1nz+gljLNYBThO5+VVm/+ZTsymd47rNmgeHQDIF7j98="

    TEST_RESULTS = ["http://adf.ly/A2x5O"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            'http://www.argentinawarez.com')

    def expand(self, url, **extra):
        link = self.get_soup(url).find('a', 'a')
        if link:
            return [link['href'], ]
        return []

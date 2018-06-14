from sandcrawler.scraper import ScraperBase


class AllRls(ScraperBase):

    TEST_URL = "http://allrls.net/fear-the-walking-dead-s02e02-720p-hdtv-x264-avs/"
    TEST_RESULTS = ["TODO"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://allrls.net")

    def expand(self, url, **extra):
        soup = self.get_soup(url)
        return [url.href for url in soup.select('.entry-content a')]


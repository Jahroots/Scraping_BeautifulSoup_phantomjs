from sandcrawler.scraper import ScraperBase


class Yify(ScraperBase):

    TEST_URL = "http://i.yify.info/CCSIqoG"
    TEST_RESULTS = ["TODO"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://i.yify.info")

    def expand(self, url, **extra):
        soup = self.get_soup(url)
        return [url.href for url in soup.select('.ellipsis.innerLR.border-left a')]


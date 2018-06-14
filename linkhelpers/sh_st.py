from requests import head
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

class ShStRedirectHelperHelper(ScraperBase):

    TEST_URL = "http://sh.st/niApP"
    TEST_RESULTS = ["https://mega.co.nz/#!d1hwkSab!v9jrNDOLwVHxxAJWoERmlZTST5rCmGezQvAFNcxVVEE"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://sh.st")

    @cacheable()
    def do_expand(self, url):
        return self.get_redirect_location(
            url,
            headers={'User-Agent': 'curl/7.35.0'},
            verify=False
        )

    def expand(self, url, **kwargs):
        return self.do_expand(url)


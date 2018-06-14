from sandcrawler.scraper import ScraperBase


class FlashX_TV(ScraperBase):
    TEST_URL = "http://www.flashx.pw/smm6yfb1en6e.html"

    TEST_RESULTS = ["http://www.flashx.tv/dl?smm6yfb1en6e"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
                          'http://www.flashx.pw')

    def expand(self, url, **extra):
        if url.startswith('http://www.flashx.pw/'):
            return ['http://www.flashx.tv/dl?' + url.split('/')[3].split('.')[0]]

        return [url]


from sandcrawler.scraper import ScraperBase
import urlparse


class BoydevkaRu(ScraperBase):

    TEST_URL = "http://www.boydevka.ru/vk.php?pl=http%3A%2F%2Fvk.com%2Fvideo_ext.php%3Foid%3D10379296%26id%3D159780123%26hash%3Dc45d1d9d3b16b702%26sd"

    TEST_RESULTS = ["http://vk.com/video_ext.php?oid=10379296&id=159780123&hash=c45d1d9d3b16b702&sd"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            'http://www.boydevka.ru')

    def expand(self, url, **extra):
        qs = urlparse.parse_qs(urlparse.urlsplit(url).query)
        if 'pl' in qs:
            return qs['pl']
        return []




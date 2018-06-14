from sandcrawler.scraper import ScraperBase

class DownloadStubeNet(ScraperBase):

    TEST_URL = "http://www.download-stube.net/extern-Switched.at.Birth.S01E29.The.Trial.GERMAN.DUBBED.WS.WEBRip.x264-TVP/go-DDLs-399082034-3.html"

    TEST_RESULTS = ["http://share-links.biz/_4bmfkanqfnaf"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            'http://www.download-stube.net')

    def expand(self, url, **extra):
        links = []
        for soup in self.soup_each([url, ]):
            for iframe in soup.select('iframe'):
                links.append(iframe['src'])
        return links
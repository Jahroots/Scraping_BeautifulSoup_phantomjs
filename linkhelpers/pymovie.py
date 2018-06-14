from sandcrawler.scraper import ScraperBase


class PyMovie(ScraperBase):
    TEST_URL = 'http://movielink.pymovie.net/yzphg/'
    TEST_RESULTS = ['http://uploaded.net/file/k1k7jrya/30018D.part1.rar',
                    'http://uploaded.net/file/mqhitoc5/30018D.part2.rar',
                    'http://uploaded.net/file/wtx1yojz/30018D.part3.rar']

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://movielink.pymovie.net")

    def expand(self, url, **extra):
        soup = self.get_soup(url)
        return [lnk.href.strip() for lnk in soup.select('.links > li > a')]

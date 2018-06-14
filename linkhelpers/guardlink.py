from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

class GuardLink(ScraperBase):
    TEST_URL = 'http://guardlink.org/VIzzl1'
    TEST_RESULTS = ['http://turbobit.net/wd1z2qjp310e.html']

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://guardlink.org')

    def expand(self, url, **extra):
        return self._do_expand(url)

    @cacheable()
    def _do_expand(self, url):
        soup = self.get_soup(
            url,
            headers={'Referer': url}
        )
        results = []
        for iframe in soup.select('iframe'):
            results.append(iframe['src'])
        return results

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

import re

class PasteBinHelper(ScraperBase):

    TEST_URL = 'http://pastebin.com/BZ1JqdkP'
    TEST_RESULTS = ['http://news.ycombinator.com', 'http://slashdot.org']

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://pastebin.com')

    def expand(self, url, **extra):
        return self._do_expand(url)

    @cacheable()
    def _do_expand(self, url):
        text = ""

        if re.search(r'https?://pastebin.com/raw\?i=', url) or \
            re.search(r'https?://pastebin.com/raw/', url):
            r = self.get(url, allowed_errors_codes=[404,])
            text = r.text
        else:
            m = re.match(r'https?://pastebin.com/(.*)$', url)
            if m:
                id = m.groups()[0]
                id = id.replace("/", "")
                r = self.get("http://pastebin.com/raw?i=%s" % id, allowed_errors_codes=[404,])
                text = r.text

        if 'This page is no longer available' in text:
            return None

        links = []
        for link in self.util.find_urls_in_text(text, skip_images=True):
            links.append(link)
            if len(links) > 100:
                self.log.warning('Capped pastebin expansion at 100 for url %s', url)
                return links
        return links


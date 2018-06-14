from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

import re

class RedirectHelper(ScraperBase):

    URLS = (
        # xup.pl addresses are in the form <hex-string>.<osp-label>.xup.pl
        # NOTE: It might be worth caching this <osp-label> => <osp-link> relationship
        re.compile('http://(.*)\.xup\.pl'),

        'https://safelinking.net',
        'http://safelinking.net',
        'http://ul.to',
        'http://bit.ly',
        'http://gftxra.net',
        'http://rg.to', # Rapidgator
        'http://nontonmovie.com/file.php',
        'http://cloudzilla.to',
        'http://sharecash.org',

    )

    def setup(self):
        for url in self.URLS:
            self.register_url(ScraperBase.URL_TYPE_AGGREGATE, url)

    def expand(self, url, **extra):
        return self._do_expand(url)


    @cacheable()
    def _do_expand(self, url):
        session = self.http_session()

        resp = session.get(url, allow_redirects=False)

        if resp.status_code in (301, 302):
            new_url = resp.headers.get('Location')
            return [new_url]

        return []

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

import re
import base64


class AdflyHelper(ScraperBase):

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://adf.ly')
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://adfoc.us')
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://j.gs')

    def expand(self, url, **extra):
        return self.do_expand(url)

    @cacheable()
    def do_expand(self, url):

        resp = self.get(url, allow_redirects=False)

        if resp.status_code == 200 and 'ysmm' in resp.content:
            extracted = self._extract_from_ysmm(resp.content)
            if extracted:
                return [extracted]

        # TODO: follow redirects? See the perl code below:
        '''
        if ($resp->code == 302 and $resp->header('Location') =~ m{/ad/locked}) {
            $resp = $ua->get( $resp->header('Location') );
        }

        return $resp->header('Location') if $resp->code == 302;
        '''

        return []

    def _extract_from_ysmm(self, content):
        m = re.search('ysmm\s*=\s*[\'\"]([^\'\"]+)[\'\"]', content)
        if not m:
            return None

        contents = m.groups()[0]

        # Algorithm copied from UrlTools.pm::__adf_ly
        C, h = ('', '')
        for idx in range(len(contents)):
            if idx % 2 == 0:
                C += contents[idx]
            else:
                h = contents[idx] + h

        encoded = C + h

        try:
            decoded = base64.b64decode(encoded)
            decoded = decoded[2:]
        except TypeError:
            self.submit_parse_error("obfuscation decoding failed") # TODO: IMPROVE this
            return None

        return decoded
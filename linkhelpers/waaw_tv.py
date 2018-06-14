from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import AntiCaptchaMixin
from sandcrawler.scraper.caching import cacheable

from urlparse import parse_qs, urlparse


class WaawTvHelper(
    CloudFlareDDOSProtectionMixin,
    AntiCaptchaMixin,
    ScraperBase):

    BASE_URL = "http://waaw.tv/"
    TEST_URL = "http://waaw.tv/watch_video.php?v=N1775Y5UGNYK"
    TEST_URL = 'http://waaw.tv/watch_video.php?v=9DU9K83B8XO8'

    RECAPKEY = '6Lf3QCgTAAAAAP6NFNRGuPt8R9t1iX_NNIB4QrLk'
    TEST_RESULTS = [""]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://waaw.tv')
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def expand(self, url, **extra):
        return self.expand_link(url)

    @cacheable()
    def expand_link(self, url):

        print 'expanding...'

        # First get the URL, to make sure CF cookies are good.
        self.get(
            url,
            allowed_errors_codes=[404, ]
        )

        # Then add this to get the sub-frame
        if 'datat=1' not in url:
            url = url + '&datat=1'

        # Fetch a token, and POST it back.
        token = self.get_recaptcha_token()
        data = parse_qs(urlparse(url).query)
        data['g-recaptcha-response'] = token

        response = self.post(
            url,
            data=data,
            allowed_errors_codes=[404,]
        )

        # Then suck out iframes from that.
        links = []
        if response.text:
            soup = self.make_soup(response.text)
            for iframe in soup.select('iframe'):
                links.append(iframe['src'])
        return links

    def _get_cloudflare_action_url(self):
        return 'http://waaw.tv/robots.txt'
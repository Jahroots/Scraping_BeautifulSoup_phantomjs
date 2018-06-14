from sandcrawler.scraper import ScraperBase


class TumejorserieCom(ScraperBase):

    TEST_URL = "http://tumejorserie.com/descargar/url_encript.php?link=%20%20https://mega.co.nz/$!XRtBHKCI!acyu9iY-ZcnFMECss1ptMjwvgZGv7MJPNEh_o8shwW4"

    TEST_RESULTS = ["https://mega.co.nz/#!XRtBHKCI!acyu9iY-ZcnFMECss1ptMjwvgZGv7MJPNEh_o8shwW4"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            'http://tumejorserie.com/')

    def expand(self, url, **extra):
        # Note, there may be more replaces needed - this works for
        # things we know about, for now.
        link_at = url.find('link=')
        if link_at:
            destination = self.util.unquote(url[link_at + 5:])\
                .strip()\
                .replace('$', '#')
            return [destination, ]
        return []


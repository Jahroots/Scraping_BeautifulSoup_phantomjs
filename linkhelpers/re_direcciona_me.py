from scraper import ScraperBase


class ReDireccionaMe(ScraperBase):

    TEST_URL = "http://re-direcciona.me/r/VjFaV2IxVXdNVWhVYTFacFRURndUbFJYTVRObFZtdDNXa1ZrYkdKV1NrbFdiR2hYVjJzeGNXSkVRbFZTUlRWaFdrY3hVMUp0VmtsVmJGWlRZa2QwTkZaV1kzaFViRUpTVUZRd1BRPT0rUA=="
    TEST_RESULTS = ["http://ivpaste.com/v/tLmLV5Bc"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://re-direcciona.me')

    def expand(self, url, **extra):
        links = []

        url = url.replace("/r/", "/o/")

        soup = self.get_soup(url)

        iframes = soup.select('iframe')
        for iframe in iframes:
            url = iframe['src']
            links.append(url)

        return links

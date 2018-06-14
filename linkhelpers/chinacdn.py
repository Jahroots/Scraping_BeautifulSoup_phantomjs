import re

from sandcrawler.scraper import ScraperBase

class ChinaCDN(ScraperBase):

    TEST_URL = "http://embed.china-cdn88nmbwacdnln8hq8qwe.com/embed.php?mid" \
               "=73081"

    TEST_RESULTS = [
        "http://ufs4.china-cdn88nmbwacdnln8hq8qwe.com/view"
        "/0QxJouFA4x_MNmpSk6EFeg/1436887401%2F73081.mp4"
        ]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            re.compile('https?://embed\.china-cdn.*\.com/embed\.php'))

    def expand(self, url, **extra):
        links = []
        # First suck out the iframe
        for soup in self.soup_each([url, ]):
            for iframe in soup.select('iframe'):
                # Then get flashvar style file out.
                for iframe_content in self.get_each([iframe['src'], ]):
                    for link in self.util.find_file_in_js(iframe_content):
                        links.append(self.util.unquote(link))
        return links
from sandcrawler.scraper import ScraperBase

class PastedCoHelper(ScraperBase):

    TEST_URL = 'http://pasted.co/26a85ae6'
    TEST_RESULTS = ['http://news.ycombinator.com']

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://pasted.co')
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://tinypaste.com')

    @staticmethod
    def _parse_links_frame(soup):
        paste = soup.select('#thepaste')[0].text
        urls = map(lambda item: item.strip(), paste.split())
        urls = filter(lambda item: item.startswith("http"), urls)
        return urls

    def expand(self, url, **extra):
        soup = self.get_soup(url)

        if "Password Required" in soup.text:
            if 'password' not in extra:
                self.log.warning("Encountered link with password but no password available")
                return []

            password = extra['password']

            field_name = ''
            field = soup.select("form input")
            for field in field:
                if field['type'] == 'password':
                    field_name = field['name']
            if field_name:
                soup = self.post_soup(url, data={field_name: password}, headers={'Referer': url})
                if "Password Required" in soup.text:
                    self.log.error("Incorrect link password")
                    return []
            else:
                self.log.error("Could not extract password field name from page")

        links = []

        iframes = soup.select('iframe')

        for frame in iframes:
            src = frame['src']
            if src.startswith('http://pasted.co'):
                soup = self.get_soup(src)
                links.extend(self._parse_links_frame(soup))

        return links

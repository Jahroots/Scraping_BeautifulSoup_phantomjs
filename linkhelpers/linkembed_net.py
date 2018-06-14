from scraper import ScraperBase


class LinkEmbedNetHelper(ScraperBase):

    TEST_URL = "http://www.linkembed.net/watch.php?idl=http://www.linkembed.net/novamov.php?vid=b9fc771db13fd"
    TEST_RESULTS = ["http://embed.novamov.com/embed.php?width=600&height=480&v=b9fc771db13fd&px=1"]

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://www.linkembed.net/")

    def expand(self, url, **extra):
        if '/watch.php' not in url:
            return []

        urls = []

        soup = self.get_soup(url)

        for frame in soup.select('frame'):
            inner_url = frame.get('src')
            if '/ads.php' in inner_url:
                continue
            item_soup = self.get_soup(inner_url, headers={'Referer':url})
            for iframe in item_soup.select('iframe'):
                iframe_src = iframe.get('src')
                urls.append(iframe_src)

        return urls


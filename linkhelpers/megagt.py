from scraper import ScraperBase
from scraper import ScraperFetchException, ScraperFetchProxyException

import re


class MegaGtHelper(ScraperBase):
    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, "http://megagt.com/embed")

    def expand(self, url, **extra):
        headers = {'Referer': 'http://www.ecfilmes.com/'}  # Friendly site that often embeds from MegaGt
        soup = self.get_soup(url, headers=headers)
        urls = []
        # IMPROVE: Not all things will be slurp; it'll be up to jdownloaded to deal with it otherwise
        for script in soup.select('script'):
            m = re.findall("addiframe\('(.*)'\)", script.text)
            for result in m:
                if result.startswith("http"):
                    urls.append(result)

        return urls

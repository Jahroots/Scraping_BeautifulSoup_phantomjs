# coding=utf-8

import urlparse

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, DuckDuckGo


class Cuevana2Tv(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'https://www.cuevana2.tv'
    OTHERS_URLS = ['http://www.cuevana2.tv']
    NO_RESULTS_KEYWORD = 'hhh@$>'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for site in (self.BASE_URL,):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _parse_parse_page(self, soup):
        # Uses
        for iframe in soup.select('div.tab_container iframe'):
            submitted = False
            if iframe['src'].startswith(self.BASE_URL) or \
                    iframe['src'].startswith('http://cuevana2.tv'):
                # Try and unobfuscate
                qs = urlparse.parse_qs(urlparse.urlsplit(iframe['src']).query)
                if 'file' in qs:
                    for link in qs['file']:
                        if link.startswith('http'):
                            self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=link)
                            submitted = True
                        else:
                            self.log.debug('Unknown file type: %s', link)
            if not submitted:
                # Otherwise just submit it for now.
                # IMPROVE
                link = iframe['src']
                if link.startswith('//'):
                    link = 'http:'+iframe['src']
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         )

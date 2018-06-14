# -*- coding: utf-8 -*-
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin


class DomkinoKz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://domkino.kz'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.shorttts a.finallq'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()

        iframe_link = soup.select_one('div#tab1 iframe')['src']

        self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe_link,
                link_title=title
        )


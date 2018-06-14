# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ThePirateBay(SimpleScraperBase):
    BASE_URL = 'https://thepiratebay.org'

    OTHER_URLS = []


    def setup(self):
        self.search_term_language = 'eng'

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_P2P)

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/%s/0/99/200' % \
            self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        next = soup.find('img', attrs={'alt': 'Next'})
        if next:
            return self.BASE_URL + next.parent.href
        return None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('table#searchResult tr div.detName a'):
            any_results = True
            self.submit_search_result(
                link_url=self.BASE_URL + result.href,
                link_title=result.text
            )
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # grab magnet link.
        magnet = soup.select_one('div.download a')
        if magnet:
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=magnet.href,
                link_title=magnet.text,
            )


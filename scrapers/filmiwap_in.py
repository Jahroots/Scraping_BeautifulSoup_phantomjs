# -*- coding: utf-8 -*-
import urlparse

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmiWapIn(SimpleScraperBase):
    BASE_URL = 'http://filmiwap.uclip.mobi'
    OTHER_URLS = ['http://filmiwap.in']

    LONG_SEARCH_RESULT_KEYWORD = 'dvd'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):

        return self.BASE_URL + '/search/index.xhtml?keyword=' + search_term

    def _fetch_no_results_text(self):
        return u'sorry the results you need not found'

    def _fetch_next_button(self, soup):
        pagination = soup.select_one('ul.pagination')
        if not pagination:
            return None
        link = pagination.find('a', text='>')
        if link:
            return self.BASE_URL + link.href
        return None

    def _parse_search_result_page(self, soup):
        for link in soup.select('.media-heading a'):
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link.text
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        for link in soup.select('#videoinfo01 .table a'):
            href = self.get_redirect_location(self.BASE_URL + link.href)

            if not href:
                continue

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=href,
                link_title=link.text,
                )


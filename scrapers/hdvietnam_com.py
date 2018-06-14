# -*- coding: utf-8 -*-

import re
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase

class HDvietnam(SimpleScraperBase):
    BASE_URL = 'http://www.hdvietnam.com/'

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'vie'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/233686/?o=date&c[title_only]=1&q=' + search_term

    def _fetch_no_results_text(self):
        return u'Không có Kết quả nào'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text=u'Tiếp >')
        if next:
            return self.BASE_URL + next.href
        return None

    def search(self, search_term, media_type, **extra):
        data = {
            'keywords': search_term,
            'users': '',
            'date': '',
            'nodes[]': '',
            'child_nodes': 1,
            'order': 'date',
            '_xfToken': '',
            '_xfRequestUri': 'search/',
            '_xfNoRedirect': 1,
            '_xfResponseType': 'json',
        }
        response = self.post(
            self.BASE_URL + 'search/search',
            data=data
        )

        json_data = response.json()
        if 'message' in json_data and json_data['message'] == u'Không tìm thấy.':
            self.submit_search_no_results()
            return
        elif '_redirectTarget' in json_data:
            self._parse_search_result_page(
                self.get_soup(
                    json_data['_redirectTarget']
                )
            )


    def _parse_search_result_page(self, soup):
        for result in soup.select('ol.searchResultsList li h3.title a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text,
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            self._parse_search_result_page(
                self.get_soup(next_button)
            )

    def _parse_parse_page(self, soup):
        for content in soup.select('div.messageContent'):
            for url in self.util.find_urls_in_text(unicode(content)):
                if '.jpg' in url or 'imgbox' in url or 'subscene' in url or '.png' in url or 'imgur' in url or\
                                'hdvietnam' in url or u'http://cập' in url or '/reviews/' in url or 'news.php' in url\
                                 or 'store.' in url:
                    continue

                self.submit_parse_result(
                    link_url=url,
                )

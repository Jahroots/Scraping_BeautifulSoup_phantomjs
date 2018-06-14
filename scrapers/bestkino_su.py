# coding=utf-8

import json
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import OpenSearchMixin, SimpleScraperBase
import json
class BestKinoSU(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.kinoxouse.org'
    OTHER_URLS = ['http://kino-for.me', 'http://kinofor.me', 'http://bestkino.me', 'http://bestkino.su']

    LONG_SEARCH_RESULT_KEYWORD = u'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

        self._request_response_timeout = 400
        self._request_connect_timeout = 300


    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def _fetch_search_url(self, search_term):
        return self.BASE_URL + '/search?x=0&y=0&q={}'.format(search_term)

    def _parse_search_results(self, soup):
        links = soup.select('table.eBlock div.eTitle a')
        if not links and len(links) == 0:
            return self.submit_search_no_results()

        for link in links:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )
        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_results(soup)


    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        return 'http:' + link['href'] if link else None



    def _fetch_no_results_text(self):
        return u'По вашему запросу мы ничего не нашли'


    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        season = episode = None
        title = soup.select_one('h1')
        series = soup.select_one('div.numser')
        if title:
            title = title.text

        if series:
            series = series.text
            season, episode = self.util.extract_season_episode(series)

        iframes = soup.select('iframe[allowfullscreen]')
        for iframe in iframes:
            src = iframe['src']
            if src:
                if 'http' not in src:
                    src = 'http:' + src
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= src,
                    link_title=title,
                    series_season=season,
                    series_episode=episode,
                )
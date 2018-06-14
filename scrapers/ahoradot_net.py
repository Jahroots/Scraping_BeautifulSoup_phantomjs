# -*- coding: utf-8 -*-

import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Ahoradot(SimpleScraperBase):
    BASE_URL = 'http://ahoradot.net'
    OTHER_URLS = ['http://www.ahoradot.net']
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    #  vBulletin™ גרסה 5.1.7

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'heb'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        self.media_type = media_type
        self.found = 0

        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + search_term

    def _parse_search_result_page(self, soup):
        results = soup.select('#main_content article')

        for result in results:
            link = result.select_one('h2 a')
            h2 = result.select_one('h2')

            if self.search_term.decode('utf') in h2.text:
                self.found = 1
                self.submit_search_result(
                    link_url=link['href'].encode('ascii', 'ignore').decode('ascii'),
                    link_title=link['title'],
                    image = self.util.find_image_src_or_none(result, 'img')
                )

        if self.found == 0:
           return self.submit_search_no_results()


    def _fetch_no_results_text(self):
        return u'התוכן נגיש רק לחברים רשומים או שאין תוכן להצגה'

    def _fetch_next_button(self, soup):
        nxt = soup.select_one('div.pagination a.nextpage')
        if nxt and self.found == 1:
          return nxt['href'].encode('ascii', 'ignore').decode('ascii')
        else:
            return None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)
        results = self.util.find_urls_in_text(soup.select_one('div.entry-content').text)

        if results:
            for link in results:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link.encode('ascii', 'ignore').decode('ascii'),
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )


        results = soup.select('div.mb_link_hld p a')
        for link in results:
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link.href,
                link_title=title,
                series_season=series_season,
                series_episode=series_episode,
            )
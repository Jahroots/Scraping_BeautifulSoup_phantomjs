# coding=utf-8

import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Elmejoranime(SimpleScraperBase):
    # SMF forum

    BASE_URL = 'http://www.elmejoranime.org'
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'HDTV'
    SINGLE_RESULTS_PAGE = True  # in reality - no

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s={}'.format(search_term)


    def _fetch_no_results_text(self):
        return u"Nada encontrado"

    def _parse_search_result_page(self, soup):

        for result in soup.select("article h2.entry-title"):
            result = result.select_one('a')
            self.submit_search_result(link_title=result.get('title'),
                                          link_url=result.get('href'))

    def _fetch_next_button(self, soup):
        links = soup.select('.navPages')
        if links:
            next_link = [l for l in links if l.text == str(curr_page + 1)]
            if next_link:
                return next_link[0].href

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for box in soup.select('div.entry-content p a'):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=box.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

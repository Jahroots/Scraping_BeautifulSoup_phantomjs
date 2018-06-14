# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Lirenwo(SimpleScraperBase):
    BASE_URL = 'http://lirenwo.com'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?submit=Find&s=' + search_term

    def _fetch_next_button(self, soup):
        nxt = soup.select_one('#olderEntries a')
        self.log.debug('-------------------')
        return nxt.href if nxt else None

    def _fetch_no_results_text(self):
        return 'Sorry, but you are looking for something that isn\'t here'

    def _parse_search_result_page(self, soup):
        found = False

        for link in soup.select('.postTitle a'):
            found = True
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.postTitle').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.down a'):

            if link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=link.text,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

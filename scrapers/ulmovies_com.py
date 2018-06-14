# -*- coding: utf-8 -*-

import time

from sandcrawler.scraper import ScraperBase, ScraperFetchException
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Ulmovies(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://ulmovies.com'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 0, tv 0'

    def get(self, url, **kwargs):
        try:
            return super(Ulmovies, self).get(url, **kwargs)
        except ScraperFetchException:
            self.log.warning('Sleeping and retrying.')
            time.sleep(10)
            return super(Ulmovies, self).get(url, **kwargs)

    def _parse_search_result_page(self, soup):
        for link in soup.select('.main-news h2 a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.quote a'):
            if not link.href.startswith(self.BASE_URL) and link.href.startswith('http') and 'http://www.imdb.com' not in link.href:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmIkz(SimpleScraperBase):
    BASE_URL = 'https://filmikz.ch'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?search={}&image.x=27&image.y=10'.format(search_term)

    def _fetch_no_results_text(self):
        return 'Total movies'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='››')
        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.main a')[:-1]:
            found = True
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link['href'].split('/')[-1].replace('-', ' ')[:-8],
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('a'):
            if link.href and link.href.startswith('/w.php'):
                url = link.href[9:]

                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=url.decode('base-64').strip(),
                    link_text=title,
                    series_season=series_season,
                    series_episode=series_episode,
                    )

# coding=utf-8
import re
import json
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class KinofluxNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinoflux.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            u'{}/engine/mod_gameer/search/frontend/ajax_search.php'.format(self.BASE_URL),
            data={
                'query': search_term,
            }
        )

        found = False
        for result in soup.select('a'):
            self.submit_search_result(
                link_url=result.href,
                link_text=result.text,
            )
            found = True

        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.playerCode iframe'):
            url = link['src']
            self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=title.text,
                        series_season=series_season,
                        series_episode=series_episode,
            )

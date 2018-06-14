# coding=utf-8
import re
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HdserialsTv(SimpleScraperBase):
    BASE_URL = 'http://www.hdserials.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/serialy/itemlist/search/73.html?searchword={search_term}&categories=&format=html&tpl=search'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li.pagination-next a')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found = True
        for result in soup.select('h2.genericItemTitle a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
            )
            found = True
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            title = title.text
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe in soup.select('div.itemBody iframe'):
            self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=iframe['src'],
                        series_season=series_season,
                        series_episode=series_episode,
            )

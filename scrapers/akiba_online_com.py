# coding=utf-8

import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class AkibaOnlineCom(SimpleScraperBase):
    BASE_URL = 'https://www.akiba-online.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _fetch_search_url(self, search_term, media_type):
        return None

    def _fetch_no_results_text(self):
        return u'No results found'

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            self.BASE_URL + '/search/search', data = {'keywords' : search_term}
        )
        self._parse_search_results(soup)

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Next >')
        if next_button:
            return self.BASE_URL+'/'+next_button.href
        return None

    def _parse_search_results(self, soup):
        if '_redirectTarget' in soup.text:
            redirect_url = json.loads(soup.text)['_redirectTarget']
            soup = self.get_soup(redirect_url)
        if 'No results found.' in soup.text:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if self.can_fetch_next() and next_button_link:
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3.title'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('a.externalLink'):
            if 'http' in link.text:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

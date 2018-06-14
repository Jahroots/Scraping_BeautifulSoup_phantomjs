# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import json


class WatchepisodesCo(SimpleScraperBase):
    BASE_URL = 'http://www.watchepisodeseries.com/'
    OTHER_URLS = ['http://www.watchepisodes.co/', ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'No content available'

    def _fetch_search_url(self, search_term, media_type=None):
        return self.BASE_URL + 'search/ajax_search?q={}'.format(search_term)

    def _parse_search_results(self, soup):
        results_text = json.loads(soup.text)
        no_results_text = results_text['genres']
        if not no_results_text:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup.text)

    def _parse_search_result_page(self, soup):
        series_list = json.loads(soup)['series']
        genres_list = json.loads(soup)['genres']
        movies_list = series_list + genres_list
        for movie_links in movies_list:
            movie_url = movie_links['seo']
            soup = self.get_soup(self.BASE_URL+movie_url)
            for links in soup.select('div.el-item  a'):
                self.submit_search_result(
                            link_title=links['title'],
                            link_url=links['href']
                        )

    def _parse_parse_page(self, soup):
        for link in soup.select('a.site-link'):
            url = link['data-actuallink']
            season, episode = self.util.extract_season_episode(soup.find('h2').text)

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=soup.find('h2').text,
                                     series_season=season,
                                     series_episode=episode
                                     )
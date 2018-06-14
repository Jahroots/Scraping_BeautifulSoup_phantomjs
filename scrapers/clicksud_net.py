# coding=utf-8
import json
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ClicksudNet(SimpleScraperBase):
    BASE_URL = 'http://www.clicksud.org'
    OTHER_URLS = ['http://wwww.clicksud.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    PARSE_RESULTS_FROM_SEARCH = True
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(ClicksudNet, self).setup()
        self._request_response_timeout = 400
        self._request_connect_timeout = 400

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/feeds/posts/default?alt=json-in-script&q={search_term}&max-results=10'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = None
        try:
            results = json.loads(soup.text.split('"feed":')[-1].split('});')[0])['entry']
        except KeyError:
            pass
        if not results:
            return self.submit_search_no_results()
        for result in results:
            alternate_link = result['link'][-1]
            content = self.make_soup(result['content']['$t']).select('iframe')
            series_season, series_episode = self.util.extract_season_episode(alternate_link['title'])
            for link in content:
                movie_link = link['src']
                if 'http' not in link['src']:
                    movie_link = 'http:'+ link['src']
                self.submit_parse_result(
                    index_page_title=alternate_link['title'],
                    link_url=movie_link,
                    link_title=alternate_link['title'],
                    series_season=series_season,
                    series_episode=series_episode,
                )

            self.submit_search_result(
                    link_url=alternate_link['href'],
                    link_title=alternate_link['title'],
                    image=None,
                )

        time.sleep(3)
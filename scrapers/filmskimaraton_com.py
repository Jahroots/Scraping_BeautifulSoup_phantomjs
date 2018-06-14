# -*- coding: utf-8 -*-
import time
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin


class FilmskimaratonCom(VBulletinMixin, SimpleScraperBase):
    BASE_URL = 'http://filmskimaraton.com'
    LONG_SEARCH_RESULT_KEYWORD = 'santa'
    SINGLE_RESULTS_PAGE = True
    USER_NAME = 'Elons1997'
    PASSWORD = 'aer0NeuWeet'
    EMAIL = 'rickyamontano@armyspy.com'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'cro'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _login_success_string(self):
        return None

    def _fetch_no_results_text(self):
        return u'Ništa nije pronađeno'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self.get_soup(
            self.post_soup(self.BASE_URL + '/search.php?do=process',
                           data={'securitytoken': 'guest',
                                 'do': 'process',
                                 'query': search_term,
                                 'submit.x':0,
                                 'submit.y':0
                                 }
                           ).select_one('form')['action'])
        )

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3.searchtitle a'):
            season, episode = self.util.extract_season_episode(result.text)
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for item in soup.select('div.article a'):
            if 'http' in item.text:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=item.text,
                                         link_title=title.text,
                                         series_season=series_season,
                                         series_episode=series_episode
                                         )

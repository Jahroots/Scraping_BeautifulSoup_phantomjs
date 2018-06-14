# -*- coding: utf-8 -*-
import time
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin


class NaszeKinoPl(VBulletinMixin, SimpleScraperBase):
    BASE_URL = 'https://www.nasze-kino.eu'
    OTHER_URLS = ['http://nasze-kino.pl', 'http://nasze-kino.pl']
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    USER_NAME = 'Holl1996'
    PASSWORD = 'BohmieCh7'
    EMAIL = 'jameytwatts@rhyta.com'

    USER_AGENT_MOBILE = False
    TRELLO_ID = 'uHEuhFgj'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'pol'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _login_success_string(self):
        return 'Mój profil'

    def _fetch_no_results_text(self):
        return None#u'Niestety - brak wyników'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else None


    def search(self, search_term, media_type, **extra):

        security_token, soup = self.login()
        self._parse_search_results(
            self.post_soup(
                '{}/search.php?do=process'.format(self.BASE_URL),
                data={
                    'securitytoken': security_token,
                    'do': 'process',
                    'query': search_term,
                    'submit.x': 4,
                    'submit.y': 11,
                },
            ))

    def login(self):
        # Log in
        soup = self.get_soup(self.BASE_URL)

        if soup.select_one('#navbar_loginform input[name="securitytoken"]'):
            self.log.debug(soup.select_one('#navbar_loginform input[name="securitytoken"]')['value'])
            soup = self.post_soup(self.BASE_URL + '/login.php?do=login', data = {'securitytoken' : soup.select_one('#navbar_loginform input[name="securitytoken"]')['value'],
                                                                                  'do': 'login',
                                                                                  'vb_login_username' : self.USER_NAME,
                                                                                  'vb_login_password' : self.PASSWORD
                                                                                 })


        security_token = soup.text.split('SECURITYTOKEN =')[1].split(';')[0].replace('"', '')
        return security_token, soup


    def parse(self, parse_url, **extra):
        security_token, soup = self.login()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('h3.searchtitle a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
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
        title = soup.select_one('font[size="3"]')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for item in soup.select('pre.bbcode_code'):
            for link in self.util.find_urls_in_text(item.text):
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=link,
                                         link_title=title.text,
                                         series_season=series_season,
                                         series_episode=series_episode
                                         )

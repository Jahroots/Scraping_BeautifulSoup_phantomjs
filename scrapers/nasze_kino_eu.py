# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper.caching import cacheable

class NaszeKinoEu(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.nasze-kino.online'
    OTHER_URLS = ['https://nasze-kino.online', 'http://nasze-kino.eu']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    USER_NAME = 'Holl1996'
    PASSWORD = 'BohmieCh7'
    EMAIL = 'jameytwatts@rhyta.com'
    USER_AGENT_MOBILE = False

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

    def _fetch_no_results_text(self):
        return u'Niestety - brak wyników'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[rel="next"]')
        if next_button:
            return '{}/{}'.format(self.BASE_URL, next_button.href)
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ol#searchbits a.threadstatus'):
            self.submit_search_result(
                link_url=self.BASE_URL+'/'+result.href,
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        security_token, soup = self.login()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for bbcode in soup.select('div.quote_container a[target]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=bbcode.href,
                link_title=bbcode.text,
                series_season=series_season,
                series_episode=series_episode,
            )

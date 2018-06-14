# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CachedCookieSessionsMixin


class Leaker(SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'https://leaker.se'
    OTHER_URLS = ['http://leaker.se']
    EMAIL = 'MaryLHughes@teleworm.us'
    PASS = '123456654321'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Did you mean'

    def _fetch_search_url(self, search_term, media_type):
        self._login()
        return self.BASE_URL + '/search/page/' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='next')
        self.log.debug('------------------------')
        return self.BASE_URL + next['href'] if next else None

    def _login(self):
        # self.get(self.BASE_URL)
        self.load_session_cookies()
        login_page_soup = self.get_soup(self.BASE_URL + '/join', allowed_errors_codes=[403])
        if 'Log out' not in str(login_page_soup):
            token = login_page_soup.find('input', {'type': 'hidden', 'name': "form_build_id"}).attrs['value']
            self.post(self.BASE_URL + '/join?destination', data={'form_build_id': token,
                                                                 'form_id': 'user_login',
                                                                 'name': self.EMAIL,#'zoftsjsj@boximail.com',
                                                                 'op': 'Log in',
                                                                 'pass': self.PASS,#'sands8',
                                                                 'username': ''},
                      headers={'Referer': self.BASE_URL + '/join'
                               #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:47.0) Gecko/20100101 Firefox/47.0'
                               }).text
            self.save_session_cookies()


    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.title a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )
            found = True
        if not found:
            self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        self._login()
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.page-header').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.field-item.even p a') + soup.select('.field-item.odd p a'):
            self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )


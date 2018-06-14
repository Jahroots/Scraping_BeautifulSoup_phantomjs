# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperAuthException
from sandcrawler.scraper.extras import CachedCookieSessionsMixin
import time

class Forum_HDmovie_vn(SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'http://forum.hdmovie.vn'

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'
    USERNAME = 'hdmovie@myspoonfedmonkey.com'
    PASSWORD = '123456'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        # raise NotImplementedError('auth via Google/FB needs to be implemented to login to the forum')

        self.search_term_language = 'vie'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(Forum_HDmovie_vn, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _login(self):
        self.load_session_cookies()
        home_soup = self.get_soup(self.BASE_URL + '/index.php?app=core&module=global&section=login')

        if 'logout' not in unicode(home_soup):

            self.log.debug('Logging in...')
            security_token = home_soup.find(
                'input', {'name': 'auth_key'})['value']
            login_result = self.post(self.BASE_URL + '/index.php?app=core&module=global&section=login&do=process',
                                     data={
                                         'ips_username': self.USERNAME,
                                         'ips_password': self.PASSWORD,
                                         'auth_key': security_token,
                                         'rememberMe': '1',
                                         # 'referer': self.BASE_URL + '/index.php?app=core&module=global&section=login'
                                     }
                                     )
            if login_result.text.find(
                    u'An extension required to process this request is missing'
            ) >= 0:
                raise ScraperAuthException('Failed login with %s / %s')

            self.save_session_cookies()


    def _fetch_no_results_text(self):
        return u'No results found for '

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _login_success_string(self):
        return u'Sign Out'

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        self._login()
        soup = self.get_soup(self.BASE_URL + (
            '/index.php?app=core&module=search&do=search&search_content=titles&search_term={}&search_app=forums').format(
            self.util.quote(search_term)))
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('td h4 a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text
            )

    def parse(self, parse_url, **extra):
        time.sleep(0.1)
        self._login()
        soup = self.get_soup(parse_url)
        title = '|'.join([soup_text.text.strip() for soup_text in soup.select('.bbc_center strong span span span')])
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('a.bbc_url'):
            if 'http' in link.href:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
        try:
            for link_text in soup.find('div', id='dl').find_all('div', 'message'):
                links = self.util.find_urls_in_text(link_text.text)
                for link in links:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
        except AttributeError:
            pass

        try:
            for link_text in soup.find_all('pre', 'prettyprint linenums:0'):
                links = self.util.find_urls_in_text(link_text.text)
                for link in links:
                    link = link.split('\n')[0]
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
        except AttributeError:
            pass
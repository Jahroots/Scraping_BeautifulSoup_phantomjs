# -*- coding: utf-8 -*-
import re
import hashlib
from sandcrawler.scraper.exceptions import ScraperAuthException
from sandcrawler.scraper import ScraperBase, DuckDuckGo
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import AntiCaptchaImageMixin
from sandcrawler.scraper import CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class ExvagosNet(AntiCaptchaImageMixin, SimpleScraperBase, CachedCookieSessionsMixin ):
    BASE_URL = 'http://www.exvagos1.com'
    OTHER_URLS = ['http://www.exvagos.net']
    # USERNAME = 'Waakis1940'
    # PASSWORD = 'ooBaeweghooy3'
    USERNAME = 'MooseMoose'
    PASSWORD = 'Moose6'
    EMAIL = 'exvmoose@myspoonfedmonkey.com'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False
    NO_RESULTS_KEYWORD = '@#$%'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'esp'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _login(self):
        self.load_session_cookies()
        home_soup = self.get_soup(self.BASE_URL + '/login.php?do=login')
        if 'Finalizar' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            md5_password = hashlib.md5(PASSWORD).hexdigest()
            security_token = home_soup.find(
                'input', {'name': 'securitytoken'})
            if security_token:
                security_token = security_token['value']
                self.post(self.BASE_URL + '/login.php?do=login',
                                     data={
                                            'vb_login_username': username,
                                            'vb_login_password': '',
                                            'vb_login_password_hint': '',
                                            'securitytoken': security_token,
                                            'do': 'login',
                                            'vb_login_md5password': md5_password,
                                            'vb_login_md5password_utf': md5_password,
                                            's': '',
                                            'cookieuser': 1,
                                     }
                                     )
            self.save_session_cookies()

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[522], **kwargs)

    def _fetch_no_results_text(self):
        return u'Lo siento, no se encontró ningún resultado'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else  None

    def search(self, search_term, media_type, **extra):
        self._login()
        home_soup = self.get_soup(self.BASE_URL)
        security_token = home_soup.find(
            'input', {'name': 'securitytoken'})['value']
        soup = self.post_soup(
            self.BASE_URL + '/search.php?do=process',
            data={
                'securitytoken': security_token,
                'do': 'process',
                'query': search_term,
                'showposts':0,
                's':'',
                'quicksearch':1,
                'exactname':1,
                'childforums':1
            }
        )
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        for page_link in soup.find_all('a', id=re.compile('thread_title_\d')):
            self.submit_search_result(
                link_url=page_link['href'],
                link_title=page_link.text,
            )

    @cacheable()
    def get_captcha_links(self, url):
        soup = self.get_soup(url)
        index_page_title = self.util.get_page_title(soup).encode('utf-8')
        series_season = series_episode = None
        title = soup.select_one('span[itemprop="title"]')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        results = []
        for post in soup.select('input[value="VER LINKS!!!"]'):
            block_id = post['onclick'].split("loadCaptcha('")[-1].split("');")[0].split(',')[0].strip("'")
            encrypted_match = post['onclick'].split("loadCaptcha('")[-1].split("');")[0].split(", '")[1].replace("'", '')
            captcha_result = self.solve_captcha(self.BASE_URL+'/prueba/create_image.php?blockId='+block_id)
            links = self.post_soup(self.BASE_URL+'/prueba/captcha.php',
                           data={'blockId': block_id, 'encryptedBlock': encrypted_match, 'txtCaptcha': captcha_result}).text.split('innerHTML = "')[-1].split('";')[0].split('\\n')
            for link in links:
                if 'Codigo invalido' not in link and link:
                    if 'http' not in link and '.' in link:
                        link = 'http://' + link
                    if 'http' not in link:
                        continue
                    if ' - ' in link:
                        link = link.split(' - ')[-1]
                if 'Codigo invalido' in link:
                    self.log.warning('Captcha failed.')
                    continue
                link = link.strip('\\r')
                if link:
                    results.append(dict(
                        index_page_title = index_page_title,
                        link_url = link,
                        link_title = link,
                        series_season = series_season,
                        series_episode = series_episode,
                    ))
        return results


    def parse(self, parse_url, **extra):
        if 'showthread' in parse_url:
            self._login()
            results = self.get_captcha_links(parse_url)
            if results:
                for result in results:
                    self.submit_parse_result(
                        **result
                    )

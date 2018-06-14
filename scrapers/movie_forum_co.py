# -*- coding: utf-8 -*-

import re
import hashlib
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import DeathByCaptchaMixin, CachedCookieSessionsMixin
from sandcrawler.scraper import ScraperParseException
import time

class MovieForumCo(SimpleScraperBase, DeathByCaptchaMixin, CachedCookieSessionsMixin):
    BASE_URL = 'https://www.allripped.net'
    OTHERS_URLS = ['http://movie-forum.co']
    USERNAME = 'Parpur'#'Haday1981'
    PASSWORD = 'Thi9uKahg'#'Baezah5eiWu'
    EMAIL = 'bernardklee@rhyta.com'
    #LONG_SEARCH_RESULT_KEYWORD = 'man'
    IS_LOGGED = False


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        # raise NotImplementedError('DeathByCaptcha does not deal well with '
        #     'mixed case captchas.')
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _load_js_cookies(self, url):
        self.load_session_cookies()
        self.webdriver().get(url)

        self.webdriver().find_element_by_css_selector('#frmLogin input[name="user"]').send_keys(self.USERNAME)
        self.webdriver().find_element_by_css_selector('#frmLogin input[name="passwrd"]').send_keys(self.PASSWORD)
        self.webdriver().find_element_by_css_selector('#frmLogin input.button_submit').click()

        cookies = []
        for cookie in self.webdriver().get_cookies():
                self.log.debug(cookie)
                self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()
        self.IS_LOGGED = True

    def _login(self):
        self._load_js_cookies(self.BASE_URL + '/index.php?action=login')

    def search(self, search_term, media_type, **extra):
        # Uses captcha!
        # First get the search page.
        self.load_session_cookies()

        if not self.IS_LOGGED:
            home_soup = self.get_soup(self.BASE_URL)
            if not home_soup.select_one('li.greeting'):
                self._login()

        soup = self.post_soup(
            self.BASE_URL + '/index.php?action=search2',
            data={
                'search': search_term,
                'submit' : 'Go',
                'advanced' : 0
            }
        )

        if 'Your last search was less than 5 seconds ago. Please try again later.' in soup.text:
            time.sleep(5)
            self.search(search_term, media_type, **extra)
            return

        results = soup.select('div.search_results_posts a[href*="topic"]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.select_one('div.pagesection strong')
        if link:
            link = link.findNext('a')
        self.log.debug('------------------------')
        return link['href'] if link else None


    def _parse_search_result_page(self, soup):

        results = soup.select('div.search_results_posts a[href*="topic"]')

        for row in results:
            anchor = row
            if anchor:
                self.submit_search_result(
                    link_url=anchor['href'],
                    link_title=anchor.text.strip(),
                    #image=self.util.find_image_src_or_none(row, 'td.alt1 img')
                )
        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h5').text

        for link in soup.select('div.post code.bbc_code'):
            text = link.text
            if text.find('http') != 0:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.text,
                link_title=title,
            )
    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)


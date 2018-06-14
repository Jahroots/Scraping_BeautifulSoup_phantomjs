# -*- coding: utf-8 -*-

import hashlib
import re
import time
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class IdflMe(SimpleScraperBase):
    BASE_URL = 'http://idfl.me'
    OTHER_URLS = []
    USERNAME = 'Whespers'
    PASSWORD = 'reiP1ue1'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL + '/login.php?do=login')
        if 'Log Out' not in unicode(home_soup):
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
                                            'vb_login_password_hint': 'Password',
                                            's': '',
                                            'securitytoken': security_token,
                                            'do': 'login',
                                            'vb_login_md5password': md5_password,
                                            'vb_login_md5password_utf': md5_password,
                                     }
                                     )


    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', attrs={'rel':"next"})
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
                'query': search_term.encode('ascii', 'xmlcharrefreplace').decode(),
            }
        )
        search_url = re.search('window.location = \"(.*)\"', soup.text)
        if search_url:
            search_url = search_url.groups()[0]
            soup = self.get_soup(search_url)
            time.sleep(10)
            if 'Sorry - no matches' in soup.text:
                return self.submit_search_no_results()
            self._parse_search_results(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('ol#searchbits h3.searchtitle a.title')

        for page_link in results:
                self.submit_search_result(
                    link_url=page_link['href'],
                    link_title=page_link.text,
                )

    def parse(self, parse_url, **extra):
        self._login()
        time.sleep(3)
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        for post in soup.select('div.content pre.bbcode_code'):
            for link in self.util.find_urls_in_text(post.text):
                if 'member.php?' in link or 'showthread.php?' in link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                )
# -*- coding: utf-8 -*-

import hashlib
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import ScraperParseException


class Xbox360isoCom(SimpleScraperBase):
    BASE_URL = 'http://www.xbox360iso.com'
    OTHER_URLS = []
    SINGLE_RESULTS_PAGE = True

    USERNAME = 'Thesert'
    PASSWORD = 'uo3eibaeHoo'
    LONG_SEARCH_RESULT_KEYWORD = 'Windows 10'

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
            token_element = home_soup.find(
                'input', {'name': 'securitytoken'})
            if not token_element:
                self.log.error('Could not find security token element in %s', home_soup)
                raise ScraperParseException('Could not find security token element.')
            security_token = token_element['value']

            self.post(self.BASE_URL + '/login.php?do=login',
                                     data={
                                            'vb_login_username': username,
                                            'vb_login_password': '',
                                            'vb_login_password_hint': '',
                                            'securitytoken': security_token,
                                            'do': 'login',
                                            'vb_login_md5password': md5_password,
                                            'vb_login_md5password_utf': md5_password,
                                     }
                                     )


    def _fetch_no_results_text(self):
        return 'Sorry - no matches'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else  None

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
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
            }
        )
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        for page_link in soup.select('h3.searchtitle a.title'):
            page_link_soup = self.get_soup(self.BASE_URL+'/'+page_link['href'])
            if any(nav.text == 'PC/Mac/Manga/Mobile/Music Downloads' for nav in
                   page_link_soup.select('.navbit a')):
                self.submit_search_result(
                    link_url=page_link['href'],
                    link_title=page_link.text,
                )

    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        for post in soup.select('blockquote.postcontent'):
            for link in post.select('a[rel="nofollow"]'):
                if 'href' in link.attrs:
                    link_title = link.text
                    if 'imbd' not in link.href and '.jpg' not in link.href and '.png' not in link.href:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link['href'],
                            link_title=link_title,
                        )
        for post in soup.select('pre.bbcode_code'):
            for link in self.util.find_urls_in_text(post.text):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                )
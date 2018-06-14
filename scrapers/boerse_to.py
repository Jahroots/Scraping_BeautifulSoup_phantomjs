#coding=utf-8

import json

from sandcrawler.scraper import ScraperBase, ScraperAuthException
from sandcrawler.scraper.extras import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper.extras import CachedCookieSessionsMixin


class BoerseTo(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, ScraperBase):

    BASE_URL = 'https://boerse.to'
    USERNAME = 'Whishichan'
    PASSWORD = 'uimie3Eiqu'
    EMAIL = 'JoeAHenry@jourrapide.com'

    LONG_SEARCH_RESULT_KEYWORD = 'mother'



    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "deu"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.requires_webdriver = True
        # self.webdriver_type = 'phantomjs'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, **kwargs)

    def _login(self):
        # Get the page first, with some cookies.
        self.load_session_cookies()
        # Login redirects to the main page when already logged in :)
        response = self.get(self.BASE_URL + '/login')
        if 'login' not in response.url:
            return True
        login_data = {
                'login': self.USERNAME,
                'register': 0,
                'password': self.PASSWORD,
                'redirect': self.BASE_URL + '/',
                'cookie_check': 1,
                '_xfToken': '',
                }
        response = self.post(
            self.BASE_URL + '/login/login', #[sic]
            data=login_data
        )
        if response.text.find(
            u'Du hast ein falsches Passwort eingegeben.') >= 0:
            raise ScraperAuthException('Failed to login')
        self.save_session_cookies()
        return True

    def search(self, search_term, media_type, **extra):
        self._login()
        # Grab the first page to get out a token.
        base_soup = self.get_soup(self.BASE_URL + '/search')
        token = base_soup.find('input', {'name': '_xfToken'})['value']
        search_url = self.BASE_URL + '/search/search'
        search_params = {
            'keywords': search_term,
            'nodes[]': '',
            'order' : 'last_activity',
            'type': 'post',
            'title_only': 1,
            'child_nodes': 1,
            'group_discussion': 1,
            '_xfRequestUri': '/search/',
            '_xfNoRedirect': 1,
            '_xfToken': token,
            '_xfResponseType': 'json'
        }
        response = self.post(search_url, data=search_params).json()

        if '_redirectTarget' in response:
            self._parse_search_results(
                response['_redirectTarget']
            )
        else:
            self.submit_search_no_results()


    def _parse_search_results(self, url):
        # if json_data['templateHtml'].find(
        #         u'Die Live-Suche konnte nichts finden') >= 0:
        #     return self.submit_search_no_results()

        soup = self.get_soup(url)
        for result in soup.select('div.titleText h3.title a'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + result['href'],
                link_title=result.text,
            )

        if self.can_fetch_next():
            current_page = soup.select_one('a.currentPage')
            if current_page:
                for sibling in current_page.next_siblings:
                    if sibling.name and sibling.name == 'a' and sibling.href:
                        self._parse_search_results(self.BASE_URL + '/' + sibling.href)


    def parse(self, parse_url, **extra):
        self._login()
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        # User generated content, so no real form to it.
        # Grab all links within 'blockquote.messageText'
        index_page_title = self.util.get_page_title(soup)
        for result in soup.select('blockquote.messageText a'):
            # And follow it, as many appear to be anonomized/shorteneed
            url = result['href']
            if url.startswith('/') or url.startswith(self.BASE_URL):
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=result.text
                                     )



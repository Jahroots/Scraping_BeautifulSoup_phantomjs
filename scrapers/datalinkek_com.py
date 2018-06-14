# -*- coding: utf-8 -*-

import hashlib
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin


class DatalinkekCom(SimpleScraperBase):
    BASE_URL = 'https://datalinkek.com'
    OTHER_URLS = ['http://datalinkek.com']
    USERNAME = 'Thimerse'
    PASSWORD = 'uhaungee2AeL'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'hun'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)



    def _login(self):
        home_soup = self.get_soup(self.BASE_URL + '/login.php?do=login')
        if u'Kilépés' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            md5_password = hashlib.md5(PASSWORD).hexdigest()
            security_token = home_soup.find(
                'input', {'name': 'securitytoken'})['value']
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
        return None# u'Sajnálom, nem találtam semmit'

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
        results = soup.select('div.inner h3.searchtitle')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for page_link in results:
            page_link = page_link.select_one('a')
            self.submit_search_result(
                link_url=page_link['href'],
                link_title=page_link.text,
            )

    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        post_id = soup.select_one('a.report')
        if post_id:
            post_id = post_id.href.split('p=')[-1]
            sec_token = soup.text.split('SECURITYTOKEN = "')[-1].split('";')[0]
            thanks_link_soup = self.post_soup('http://datalinkek.com/ajax.php', data={'securitytoken':sec_token, 'do':'hthanks', 'postid':post_id})
            for post in thanks_link_soup.select('pre.bbcode_code'):
                links = self.util.find_urls_in_text(post.text)
                for link in links:
                    if 'imbd' not in link and '.jpg' not in link and '.png' not in link:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link,
                            link_title=link,
                        )
            for post in soup.select('pre.bbcode_code'):
                for link in self.util.find_urls_in_text(post.text):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                    )
# -*- coding: utf-8 -*-
import time
from sandcrawler.scraper import ScraperAuthException
from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin, CachedCookieSessionsMixin


class SharethefilesCom(SimpleScraperBase, VBulletinMixin, CachedCookieSessionsMixin):
    BASE_URL = 'https://sharethefiles.com'
    USERNAME = 'srtyhfs'
    PASSWORD = 'ASDREWQsdertfc23'
    EMAIL = 'RobertCNordman@dayrep.com'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _login(self):
        soup = self.get_soup('https://sharethefiles.com/forum/ucp.php?mode=login')
        if 'Logout' not in unicode(soup):
            sid = soup.find('input', attrs={'name': "sid"})['value']
            self.post(
                self.BASE_URL + '/forum/ucp.php?mode=login',
                data={'username': self.USERNAME,
                      'password': self.PASSWORD,
                      'login': 'Login',
                      'redirect': 'index.php',
                      'sid':sid
                      }
            )

    def search(self, search_term, media_type, **extra):
        self._login()
        return super(SharethefilesCom, self).search(search_term, media_type, **extra)

    def _fetch_no_results_text(self):
        return 'No suitable matches were found.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/forum/search.php?keywords=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[rel="next"]')
        if link:
            return self.BASE_URL + '/forum' + link['href'][1:]
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.postbody h3 a'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/forum' + result['href'][1:],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for post in soup.select('a'):
            if post.href.startswith('ed2k:'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=post.href,
                    link_title=post.text,
                )


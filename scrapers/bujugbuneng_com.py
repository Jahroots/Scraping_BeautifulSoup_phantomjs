# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Bujugbuneng(SimpleScraperBase):
    BASE_URL = 'http://www.bujugbuneng.com'
    OTHER_URLS = ['http://bujugbuneng.com', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError

    def _fetch_search_url(self, search_term, media_type):
        return '{}/?submit=Search&s={}'.format(
            self.BASE_URL,
            self.util.quote(search_term)
        )

    def _fetch_next_button(self, soup):
        prev = soup.select_one('div.nav-previous a')
        if prev:
            return prev.href
        return None

    def _fetch_no_results_text(self):
        return 'No results were returned.'

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('h1.entry-title a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )
        if not found:
            self.submit_search_no_results()

    def resolve_redirect(self, link):
        if link.startswith('{}/out.php'.format(self.BASE_URL)):
            link_url = self.get_redirect_location(link)
            return self.resolve_redirect(link_url)
        elif link.startswith('http://bujugbuneng.com/redir.php?url='):
            return self.resolve_redirect(link[37:])
        return link



    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.entry-content a'):
            link_url = self.resolve_redirect(link.href)
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,

                    )

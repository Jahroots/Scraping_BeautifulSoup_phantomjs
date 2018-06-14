# coding=utf-8

import re

from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin, ScraperBase


class BobFilmNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://bobyfilms.net'
    OTHER_URLS = ['http://bobfilm.cc', 'http://bobfilm.club']
    LONG_SEARCH_RESULT_KEYWORD = u'война'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.search_term_encoding = 'windows-1251'

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

    def _parse_search_result_page(self, soup):

        results = soup.select('.sh3 a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            href = link['href']
            if href.startswith('/'):
                href = self.BASE_URL + href
            self.submit_search_result(
                link_url=href,
                link_title=link.text
            )

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        iframes = soup.select('div[class="box visible"] iframe')
        for iframe in iframes:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=iframe['src'],
                                     link_title=title
                                     )

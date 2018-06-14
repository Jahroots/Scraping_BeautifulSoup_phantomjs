# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HdmoviesWatch(SimpleScraperBase):
    BASE_URL = 'http://www.hdmovieswatch9.org'
    OTHER_URLS = ['http://www.hdmovieswatch2.org','http://www.watchmovies4k.org','http://www.allhdmovieswatch.org', 'http://www.hdmovieswatchs.org','http://www.hdmovieswatchs.net', 'http://www.hdmovieswatchs.net', 'http://www.hdmovieswatch.eu', 'http://www.hdmovieswatch.org', 'http://www.hdmovieswatch.net', 'http://www.hdmovieswatch.at' ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'No content available'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/page/{}/?s={}'.format(start, search_term)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('.item'):
            self.submit_search_result(
                link_title=link.h2.text,
                link_url=link.a.href
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.movieplay iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['src'])
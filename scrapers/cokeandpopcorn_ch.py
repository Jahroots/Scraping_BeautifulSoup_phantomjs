# -*- coding: utf-8 -*-
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class CokeandpopcornCh(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.cokepopcorn.ch'
    OTHER_URLS = ['http://www.cokeandpopcorn.ch']
    SINGLE_RESULTS_PAGE = True
    SEARCH_TERM = ''
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    TRELLO_ID = 'Mif661lw'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True
        self._request_response_timeout = 600
        self._request_connect_timeout = 300

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 403], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?c=movie&m=filter&keyword={}'.format(self.util.quote(self.SEARCH_TERM))

    def search(self, search_term, media_type, **extra):
        self.webdriver().get(self._fetch_search_url(search_term, media_type))
        soup = self.make_soup(self.webdriver().page_source)
        self._parse_search_result_page(soup)


    def _fetch_no_results_text(self):
        return u'Apologies, but no movies were found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):

        results = soup.select('h2.entry-title a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2')
        if title:
            title = title.text

        for movie_link in soup.select('div#player iframe'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=movie_link['src'],
                                     link_title=title
                                     )


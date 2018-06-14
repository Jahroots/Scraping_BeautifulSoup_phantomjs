# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase


class PutlockerWs(SimpleGoogleScraperBase):
    BASE_URL = 'http://www.seeitfree.org'
    OTHER_URLS = ['http://www.putlocker.ws']

    LONG_SEARCH_RESULT_KEYWORD = 'man'

    USER_NAME = 'Dayse1980'
    PASSWORD = 'Ahpee7BahT'
    EMAIL = 'carlosmalvarez@rhyta.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError('Deprecated. Not relevant information available for this.')

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return u'0 results found'

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
        for result in soup.select('.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        for result in soup.select('.fix-table a'):
            source_soup = self.get_soup(result['href'])
            link = source_soup.find('div', 'boton reloading').find('a')['href']
            title = self.util.get_page_title(soup)
            self.submit_parse_result(link_url=link,
                                     link_title=title,
                                     )

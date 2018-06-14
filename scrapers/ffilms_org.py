
# coding=utf-8

from sandcrawler.scraper import ScraperBase
import ssl
import urllib2
class FFilmsOrg(ScraperBase):
    BASE_URL = 'http://ffilms.org'

    #SINGLE_RESULTS_PAGE = True  # in reality - no

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self._request_response_timeout = 400
        self._request_connect_timeout = 300

    def get(self, url, **kwargs):
        return super(FFilmsOrg, self).get(url, allowed_errors_codes=[403],
                                               **kwargs)
    def get(self, url):
        context = ssl._create_unverified_context()
        page = urllib2.urlopen(url, context=context).read()
        return self.make_soup(page)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)

        soup = self.get(search_url)
        #for soup in self.soup_each([search_url, ]):
        self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if not soup.select('div.content-list'):
            return self.submit_search_no_results()
        for result in soup.select('div.content-list a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

        next_button = soup.select_one('a.nextpostslink')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get(
                    next_button['href'])
            )

    def parse(self, parse_url, **extra):
        #for soup in self.soup_each([parse_url, ]):
        self._parse_parse_page(self.get(parse_url))

    def _parse_parse_page(self, soup):
        for iframe in soup.select('iframe'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url='http:' + iframe['src'] if iframe['src'].startswith('//') else  iframe['src'],
                                     )

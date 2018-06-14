# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Peliculas4Tv(SimpleScraperBase):
    BASE_URL = 'http://peliculas4.mobi'
    OTHER_URLS = ['http://peliculas4.tv', ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/peliculas-online/' + search_term + '/'

    def _fetch_no_results_text(self):
        return 'Tu Busqueda no obtuvo ningun resultado'

    def _fetch_next_button(self, soup):
        # Has no pagination, but only ever returns 30 items.
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.filmcontent > table > tr a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        for iframe in soup.select('div#player22 iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + iframe['src'] if iframe['src'].startswith('//') else  iframe['src'],
                                     )

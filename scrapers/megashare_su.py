# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import OpenSearchMixin, SimpleScraperBase


class MegashareSu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://megashare.pro'
    OTHER_URLS = ['http://megasharehd.su', 'http://megashare.su']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.bunch_size = 15

    def _fetch_no_results_text(self):
        return  u'Unfortunately, site search yielded no results'

    def _parse_search_result_page(self, soup):
        rslts = soup.select('.plovkaz a')
        if not rslts:
            self.submit_search_no_results()

        for result in rslts:

            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.tab_container iframe'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link['src'])

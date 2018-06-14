# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, SimpleGoogleScraperBase



class DescargadictosCo(SimpleGoogleScraperBase,SimpleScraperBase):
    BASE_URL = 'http://descargadictos.co'
    LONG_SEARCH_RESULT_KEYWORD = 'Man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'esp'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        raise NotImplementedError('The website is deprecated')

        self.register_url(ScraperBase.URL_TYPE_SEARCH,self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING,self.BASE_URL)

    def _parse_parse_page(self, soup):
        results = soup.select('a.ext')

        for result in results:
            soup = self.get_soup(result['href'])
            link = soup.select_one('a.continuar')
            title = soup.select_one('p.titfile')
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['href'],
                link_title=title.text
            )


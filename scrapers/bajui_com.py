#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin, SimpleScraperBase

class BajuiCom(SimpleScraperBase):

    BASE_URL = 'http://www.bajuineros.com'
    OTHERS_URLS = ['http://www.bajui2.com', 'http://www.bajui.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"
        #self.requires_webdriver = True
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'No hay resultados para'

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('#nextpagination')
        if next_link:
            return self.BASE_URL + '/' + next_link.parent['href']
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.result-item div.title a')

        # Dig down to the image and back up to parent.
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )



    def _parse_parse_page(self, soup):

        iframes = soup.select('div.playex iframe')
        for iframe in iframes:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                   link_url=iframe['src']
                                   )

        links = soup.select('#downloads td a[target="_blank"]')
        for link in links:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link.href
                                     )






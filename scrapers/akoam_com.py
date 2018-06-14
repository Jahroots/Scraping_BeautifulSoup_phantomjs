# coding=utf-8

import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase, CloudFlareDDOSProtectionMixin
import time

class AkoamCom(SimpleScraperBase):
    BASE_URL = 'https://ako.am'
    OTHER_URLS = ['https://akoam.com', 'http://akoam.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'عفواً : لا توجد نتائج مشابهة'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'ako-arrow ako-left-arrow')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.akoam_result a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('a.download_btn')+soup.select('a.sub_btn show'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_text=link.text,
            )
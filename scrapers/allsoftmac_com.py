# -*- coding: utf-8 -*-

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AllSoftMac(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://allsoftmac.com'

    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'

    def _fetch_search_url(self, search_term):
        return self.BASE_URL

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.pamp-2'):
            link = result.select_one('div.name a')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'div.image img')
            )

    def _parse_parse_page(self, soup):
        body = soup.select_one('div.full-story')
        for link in self.util.find_urls_in_text(str(body)):
            if link.startswith(self.BASE_URL):
                continue
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=link,
                )

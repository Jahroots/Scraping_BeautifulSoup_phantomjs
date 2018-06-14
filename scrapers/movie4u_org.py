# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Movie4U(SimpleScraperBase):

    BASE_URL = 'https://movie4u.live'
    OTHERS_URLS = ['https://movie4u.ch', 'https://movie4u.cc', 'http://movie4u.cc']


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403], **kwargs)

    def _fetch_no_results_text(self):
        return 'No results to show with'

    def _fetch_next_button(self, soup):
        link = soup.select_one('div.resppages a span.icon-chevron-right')
        self.log.debug('------------------------')
        return link.parent['href'] if link else None

    def _parse_search_result_page(self, soup):

        results = soup.select('div.episodiotitle a')
        if not results:
            results = soup.select('div.title a')


        for result in results:
            self.submit_search_result(
                link_url = result['href'],
                link_title= result.text

            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.data h1')
        if title:
            title = title.text
        for link in soup.select('iframe[class="metaframe rptss"]'):
            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url = link['src'],
                link_title = title
            )
# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class MoviesHubTv(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://movieshub.stream'
    OTHERS_URLS = ['http://hubflex.co', 'http://movieshub.tv']

    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return u'No results to show with'

    def _fetch_search_url(self, search_term, media_type=None):
        self.page = 1
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_next_button(self, soup):
        self.page += 1
        link = soup.select_one('a.arrow_pag')
        if link:
            return link.href
        return None

    def _parse_search_result_page(self, soup):
        for link in soup.select('div.search-page div.result-item div.title a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('#option-1 iframe[class="metaframe rptss"]'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link['src'])
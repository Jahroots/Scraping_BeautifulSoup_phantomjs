# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin

#curl 'http://kinox.pe/aGET/Mirror/Dr-Strange-1&Hoster=50'
class Movies3004U(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://300mbmovies4u.club'
    OTHER_URLS = ['http://300mbmovies4u.lol', 'http://300mbmovies4u.co', 'http://300mbmovies4u.net']


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL +'/?s='+ '%s' % self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.recent-posts li h2 a')

        if not results or len(results)== 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url = result['href'],
                link_title = result['title']
            )

    def _parse_parse_page(self, soup):

        for link in soup.select('p[style="text-align: center;"] a'):
            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url= link['href'],
                link_title = link.text
            )

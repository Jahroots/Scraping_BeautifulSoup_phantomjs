# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class SeretilMe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://seretil.me'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'heb'

        raise NotImplementedError('The website is deprecated')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.select_one('a.nextpostslink')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.title h2 a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.title h2').text.strip()

        for link in soup.select('p a[target="_blank"]'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['href'],
                link_title=title
            )

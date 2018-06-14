# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import ScraperException, CloudFlareDDOSProtectionMixin, DuckDuckGo


class GnulaNu(CloudFlareDDOSProtectionMixin, DuckDuckGo, ScraperException):
    BASE_URL = 'http://gnula.nu'

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
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return 'did not match any documents'

    # def _parse_search_result_page(self, soup):
    #     found = 0
    #     for result in soup.select('h3.r a'):
    #         href = result['href']
    #         if href.startswith('/url'):
    #             try:
    #                 followed_response = self.get(
    #                     'https://www.google.com' + result['href'],
    #                     headers={
    #                         'User-Agent': self.USER_AGENT,
    #                     }
    #                 )
    #                 href = followed_response.url
    #             except ScraperException as error:
    #                 self.log.error("Scraper Error: %s", error)
    #                 continue
    #         self._handle_search_result(href, result.text)
    #         found = 1
    #     if not found:
    #         return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup, css_selector='div.contenido_tab iframe')
        for link in soup.select('div.contenido_tab a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     )

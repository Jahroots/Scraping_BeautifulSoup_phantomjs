# coding=utf-8

from sandcrawler.scraper import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase


class CineTuxOrg(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.cinetux.io'
    OTHER_URLS = ['http://www.cinetux.net', 'http://www.cinetux.org', 'http://cdn3.cinetux.net']
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
         return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _parse_search_results(self, soup):
        results = soup.select('div.details div.title')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            link = link.select_one('a')
            self.submit_search_result(
                         link_url=link['href'],
                         link_title=link.text
                     )
        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_results(soup)


    def _fetch_no_results_text(self):
         return u'Ningún resultado encontrado, por favor intentelo nuevamente.'

    def _fetch_next_button(self, soup):

         next_button = soup.select_one('i.icon-caret-right')
         if next_button:
             return next_button.parent.href
         return None

    def parse(self, parse_url, **extra):
        if 'pelicula' in parse_url:
            soup = self.get_soup(parse_url)
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)

        # First find the embedded ones
        for iframe in soup.select('div.playex iframe'):
            if 'http' in iframe['src']:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src'],
                    )

        links = soup.select('a[href*="links"]')
        for link in links:
            if 'http' in link.href:
                soup = self.get_soup(link.href)
                link = soup.select_one('a')
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                )





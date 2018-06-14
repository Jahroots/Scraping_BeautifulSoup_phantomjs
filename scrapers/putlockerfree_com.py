# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class PutlockerfreeCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://putlockerfree.video'
    OTHER_URLS = ['https://putlockerfree.im', 'https://putlockerfree.at', 'https://putlockerfree.se', 'https://putlockerfree.ws', 'https://putlockerfree.am', 'https://www.putlockerfree.cc', 'https://www.putlockerfree.live', 'https://www.putlockerfree.ms','https://putlockerfree.li', 'https://putlockerfree.la', 'https://www.putlockerfree.is',
                  'http://putlockerfree.com', 'https://www.putlockerfree.ac']

    TRELLO_ID = 'imXFQzto'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

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
        return u'No result for Search'

    def _fetch_next_button(self, soup):
        for pagination_link in soup.select('div.pagination li a'):
            if 'Next' in pagination_link.text:
                return u'{}{}'.format(self.BASE_URL, pagination_link['href'])
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search_movies?s=' + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.small-item a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1 a').text
        index_page_title = self.util.get_page_title(soup)
        for url in soup.select('ul.movie_links strong a')[1:]:
            if 'http' not in url['href']:
                continue
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=url['href'],
                                     link_title=title
                                     )

# -*- coding: utf-8 -*-
import urllib2
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmehdNet(SimpleScraperBase):
    BASE_URL = 'http://filmehd.net'
    OTHER_URLS = ['http://m.filmehd.net']
    USER_AGENT_MOBILE = False
    TRELLO_ID = 'Fj2U9l9K'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rom'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'cauta altceva :)'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.box-film li a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.select_one('img')['alt'] if result.select_one('img') else result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        results = soup.select('div[class="lazyframe lazyload--custom"]')
        for result in results:
            aux_soup = self.get_soup(self.BASE_URL + result['data-src'])
            iframe = aux_soup.select_one('iframe')
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url= iframe['src'],
                link_title=title,
            )
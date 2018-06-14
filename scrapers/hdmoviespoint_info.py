# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HdMoviesPoint(SimpleScraperBase):
    BASE_URL = 'http://hdmoviespoint.ws'
    OTHER_URLS = ['http://hdmoviespoint.club/', 'http://hdmoviespoint.info/']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Nothing found :('

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
         title = soup.select_one('h1.title').text.strip()
         input = soup.select_one('input[name="id"]')
         if input and input.has_attr('value'):

             link = 'http://' + soup.select_one('input[name="id"]')['value'] + '/HDMoviesPoint.com/' + soup.select_one('input[name="filename"]')['value']

             self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link,
                    link_title=title
                )

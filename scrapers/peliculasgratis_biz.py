# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PeliculasGratisBiz(SimpleScraperBase):
    BASE_URL = 'http://peliculasgratis.biz'
    LONG_SEARCH_RESULT_KEYWORD = 'hombre'
    OFF_PAGINATION = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        #self.webdriver_type = 'phantomjs'
        #self.requires_webdriver = ('parse',)

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type, start=None):
        self.OFF_PAGINATION = False
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente »')
        self.log.debug('------------------------')
        if self.OFF_PAGINATION:
            return None

        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.lista-peliculas li a')

        if not results or len(results) == 0:
            self.OFF_PAGINATION = True
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url= self.BASE_URL + result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.titulo-h1').text.strip()
        sources = soup.select('a.goto')
        for source in sources:
            soup1 = self.post_soup('http://peliculasgratis.biz/goto/', data={'id' : source['data-id']})
            link = soup1.text.split('document.location = "')[1].split('";')[0].strip()
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=link,
                link_title= title
            )

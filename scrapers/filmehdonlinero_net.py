# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmeHDonlinero(SimpleScraperBase):
    BASE_URL = 'https://filmehdonlinero.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rom'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('#article div a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            title = result.text
            if result.has_attr('title'):
                title = result['title']

            self.submit_search_result(
                link_url=result['href'],
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = ""
        if soup.select_one('h1.entry-title'):
            title = soup.select_one('h1.entry-title').text.strip()

        for link in soup.select('div.pvideo iframe'):
            src = link['src']
            if src.find('http') == -1:
                src = 'http:' + src

            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=src,
                link_title=title

            )

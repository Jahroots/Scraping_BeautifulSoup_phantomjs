# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PeliculaSio(SimpleScraperBase):
    BASE_URL = 'https://peliculasio.com'
    OTHERS_URLS =['http://peliculasio.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No se encontraron resultados'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente →')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.archive-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.single-h1').text.strip()

        for iframe in soup.select('div.video_holder iframe'):
            link = iframe['src'].replace('/pre.php', '')
            link_soup = self.get_soup(link)

            for source in link_soup.select('#playObj'):
                if source['href']:
                    self.submit_parse_result(
                        index_page_title = self.util.get_page_title(soup),
                        link_url=source['href'],
                        link_title=title)

    def get(self, url, **kwargs):
        return super(PeliculaSio, self).get(url, allowed_errors_codes=[404], **kwargs)
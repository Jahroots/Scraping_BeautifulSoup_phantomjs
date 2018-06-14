# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PeliculasyonkisSx(SimpleScraperBase):
    BASE_URL = 'http://www.peliculasyonkis.sx'
    LONG_SEARCH_RESULT_KEYWORD = 'super'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'
        # raise NotImplementedError('Appears to be geocoded - does grab links, '
        #     'though')
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Ninguna ficha coincide con tu busqueda'

    def _fetch_next_button(self, soup):
        # No pagination
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.col-sm-9.info-item-cat h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.titulo')
        for link in soup.select('.contenedorpelicula .hidden-xs a'):
            href = link['href']
            if href.startswith('http://track.globaltrackads.com'):
                href = self.get(href, verify=False).url  # http HEAD doent work here

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=href,
                                     link_title=title.contents[0].strip()
                                     )

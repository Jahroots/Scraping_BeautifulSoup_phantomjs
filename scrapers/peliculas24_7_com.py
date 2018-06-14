# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Peliculas247Com(SimpleScraperBase):
    BASE_URL = 'http://peliculas24-7.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Contenido no disponible'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class="fit item"]'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[itemprop="name"]').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.movieplay iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title,
            )

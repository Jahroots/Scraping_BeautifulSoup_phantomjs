# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PeliculasyoutubeCom(SimpleScraperBase):
    BASE_URL = 'http://www.depelicula.org'
    OTHER_URLS = ['http://verpelicula.tv', 'http://peliculasyoutube.com', 'http://repelis24.tv', 'http://peliculasyoutube.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    TRELLO_ID = 'e5PZ0AQm'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u' Por favor, intenta otra búsqueda'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.paginacion a[class="previouspostslink\'"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.post-outer')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for result in results:
            link = result.find('a', href=True)
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('iframe[allowfullscreen]'):
            url = link['src']
            if url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=link.text,
                )

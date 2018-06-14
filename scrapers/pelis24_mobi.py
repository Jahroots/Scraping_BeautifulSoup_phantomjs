# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class Pelis24Mobi(SimpleScraperBase):
    BASE_URL = 'https://pelis24.is'
    OTHER_URLS = ['http://pelis24.mobi', 'https://pelis24.mobi']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False
    PAGE = 0

    def _fetch_search_url(self, search_term, media_type):
        self.PAGE = 0
        return self.BASE_URL + '/search/' + self.util.quote(search_term) + '/'

    def _fetch_no_results_text(self):
        return u'0 Resultado de búsqueda, espero consigas lo que buscas'

    def _fetch_next_button(self, soup):
        self.PAGE = 1
        next_button = soup.select_one('link[rel="next"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.search-results-content li a')
        for link in results:
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(link, 'img'),
            )

    @cacheable()
    def _follow_link(self, url, referer):
        # Needs referer AND a GET.

        return self.get(
            url,
            headers={'referer': referer},
            allow_redirects=False,
        ).headers.get('Location', None)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('ul[class="nav nav-pills reprobut"] li a'):
            if link and link.has_attr('data-src'):
                url = link['data-src']
                if url.find('http') == -1:
                    url = 'http:' + url

                if url.startswith('https://pelis24.is/redirect/'):
                    url = self._follow_link(url, soup._url)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= url,
                    link_title=link.text,
                )

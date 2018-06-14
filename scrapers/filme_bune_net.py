# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import base64
class FilmeBuneNet(SimpleScraperBase):
    BASE_URL = 'http://www.filme-bune.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'yEcabzBO'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/{search_term}/'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No posts found'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Urmatoarea >')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.lista_filme li h2.titlu')

        if not results and len (results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
            )
    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        for iframe in soup.select('div[class="lazyframe custom_lazyframe"]'):
            url = iframe['data-src'].split('v=')[1]
            url = base64.decodestring(url)

            if 'http' not in url:
                url = 'http:' + url
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
            )

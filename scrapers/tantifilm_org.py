# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import requests, base64

class TantifilmOrg(SimpleScraperBase):
    BASE_URL = 'https://www.tantifilm.uno'
    OTHER_URLS = ['http://www.tantifilm.uno',  'http://www.tantifilm.top', 'http://www.tantifilm.me', 'http://www.tantifilm.org', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'T3g1Rsjo'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nothing found'

    def search(self, search_term, media_type, **extra):
        soup = self.make_soup(requests.get(self._fetch_search_url(search_term, media_type)).text)
        self._parse_search_result_page(soup)

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div#main_col div.image-film a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for results in results:

            result = results['href']
            title = results['title']
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.title-film-left h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div#wpwm-movie-links iframe')
        for result in results:
            movie_link = result['src']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            if 'data=' in movie_link:
                movie_link = base64.decodestring(movie_link.split('data=')[1])

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )

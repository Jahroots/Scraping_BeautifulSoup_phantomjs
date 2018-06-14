# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json

class AllpeliculasCom(SimpleScraperBase):
    BASE_URL = 'http://allpeliculas.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/movies/search/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nothing found'

    def _fetch_next_button(self, soup):
        return None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def search(self, search_term, media_type, **extra):
        text = self.get(self._fetch_search_url(search_term, media_type)).text
        items = json.loads(text)

        if len(items['items']) == 0:
            return self.submit_search_no_results()

        for item in items['items']:
            self.submit_search_result(
                link_url=self.BASE_URL + '/pelicula/' + item['slug'],
                link_title=item['title']
            )


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        for results in soup.select('span[data-serverid]'):
            movie_link = results['data-link']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
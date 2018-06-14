# coding=utf-8
import base64
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmikTv(SimpleScraperBase):
    BASE_URL = 'http://filmik.tv'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Deprecated. Website no longer available')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/show/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Brak wyników wyszukiwania'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for results in soup.select('h4.video-title a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.videocontent iframe')
        for result in results:
            movie_link = result['src']
            if 'php?id=' in movie_link:
                movie_link = base64.decodestring(movie_link.split('php?id=')[-1])
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class TvpelisNet(SimpleScraperBase):
    BASE_URL = 'http://www.peliculaseroticasonline.tv'
    OTHER_URLS = ['http://tvpelis.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'por favor intentelo nuevamente con palabras cortas'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Siguiente »')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        if soup.text.find(self._fetch_no_results_text()) > -1:
            return self.submit_search_no_results()

        found = 0
        for results in soup.select('div[class*="movie-preview"] div[class="movie-poster"] a'):
            self.submit_search_result(
                link_url=results['href'],
                link_title=results.text,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div iframe'):
            if 'youtube' in link['src']:
                continue

            movie_link = None
            if '/videomega' in link['src']:
                movie_link = 'http://'+link['src']
            elif 'http' not in link['src']:
                movie_link = 'http:'+link['src']




            self.log.warning(movie_link)

            if movie_link:
                movie_link = movie_link.replace('http:/p', 'http://')
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PeliculasreyCom(SimpleScraperBase):
    BASE_URL = 'http://www.peliculasrey.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Lo siento, no hay videos que se ajusten a lo que busca'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.poster a.frame'):
            result = results['href']
            title = results.find('span', 'frame-title').text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.film-title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        for movie_link in soup.select('div.usual iframe') + soup.select('ul#source-list li a'):
            try:
                movie_link = movie_link['src']
            except KeyError:
                movie_link = movie_link['rel'][0]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
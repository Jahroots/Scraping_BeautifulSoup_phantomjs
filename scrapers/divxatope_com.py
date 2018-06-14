# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DivxatopeCom(SimpleScraperBase):
    BASE_URL = 'http://www.divxatope1.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def setup(self):
        raise NotImplementedError

    def _fetch_no_results_text(self):
        return None

    def _get_search_results(self, search_term, page=1):
        return self.post_soup(
                    self.BASE_URL + '/buscar/descargas',
                    data={'search': search_term, 'categoria': '', 'subcategoria': '', 'idioma': '', 'calidad': '',
                          'ordenar': 'Fecha', 'ord': 'Descendente', 'pg': page}
                )

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        self.page = 1
        soup = self._get_search_results(search_term)
        self._parse_search_result_page(soup)
        while self.can_fetch_next():
            page_soup = self._get_search_results(search_term, page=self.page)
            if not self._parse_search_result_page(page_soup):
                break
            self.page +=1

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('ul.peliculas-box a'):
            episode_soup = self.get_soup(link['href'])
            for episode_link in episode_soup.select('ul.chapters a.chap-title'):
                self.submit_search_result(
                    link_url=episode_link['href'],
                    link_title=episode_link['title'],
                )
                found = True
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        results_download = soup.find_all('a', attrs={'class':re.compile('f1-btn\d')})
        for result_download in results_download:
            movie_soup = self.get_soup(result_download['href'])
            links = movie_soup.select('div.box5')
            for link in links:
                try:
                    movie_link = link.find('a')['onclick'].split("links=")[-1].split("',")[0]
                except KeyError:
                    movie_link = link.find('a')['href']
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=movie_link,
                                         link_title=title,
                                      )
            torrent_link = movie_soup.select_one('a.btn-torrent')['href']
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=torrent_link,
                                     link_title=title,
                                     )

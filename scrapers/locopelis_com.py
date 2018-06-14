# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class LocopelisCom(SimpleScraperBase):
    BASE_URL = 'https://www.locopelis.com'
    OTHER_URLS = ['http://www.locopelis.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    USER_AGENT_MOBILE = False

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/buscar/?q={}&page={}'.format(search_term, start)

    def _fetch_no_results_text(self):
        return u'A continuación te mostramos los resultados obtenidos para'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        rslts = soup.select('div.f_right div.peli_img_img a')
        for result in rslts:
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result['title'],
            )

        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_parse_page(self, soup):
        for iframe_link in soup.select('iframe'):
            title = soup.find('h2').text.strip()
            movie_link = iframe_link['src']
            if 'like.php?href=' in movie_link:
                movie_link = movie_link.split('=')[1]

            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_title=title,
                                     link_url=movie_link)

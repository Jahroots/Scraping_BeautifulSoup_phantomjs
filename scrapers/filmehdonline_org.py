# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmehdonlineOrg(SimpleScraperBase):
    BASE_URL = 'http://www.filmehdonline.org'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'b6YiUsHn'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Sorry, we couldn't find any results based on your search query"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Inainte »')
        return next_link['href'] if next_link else None

    def _parse_search_results(self, soup):
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.lista_filme_categorie li div.titlu a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('div.text a').text
        movie_links = soup.select('div.entry-embed iframe')
        for movie_link in movie_links:
            movie_link = movie_link['src']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=title
            )
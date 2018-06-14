# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ClubedownCom(SimpleScraperBase):
    BASE_URL = 'http://clubedanet.com'
    OTHER_URLS = ['http://clubedown.com',]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Erro 404"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Próxima Página')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.entrytitle a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        try:
            movie_links = soup.find('img', attrs={'src':re.compile("download.png")}).find_next('p').find_all('a')
        except AttributeError:
            movie_links = soup.find('div', 'entrybody').find_all('a', href=True)
        for movie_link in movie_links:

            movie_link = movie_link['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=title
            )
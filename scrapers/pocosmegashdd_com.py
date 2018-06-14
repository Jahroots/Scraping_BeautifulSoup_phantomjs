# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PocosmegashddCom(SimpleScraperBase):
    BASE_URL = 'http://www.pocosmegashd.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Lo siento, no hay videos que se ajusten a lo que busca'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Siguiente »')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.caje-index .showhim h6 a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        movie_links = soup.find('div', 'post-body-single').find_all('a', text=re.compile('Click'))+\
                     soup.find('div', 'post-body-single').find_all('h3', attrs={'style':'text-align: center'})
        for movie_link in movie_links:
            link = ''
            try:
                link = movie_link['href']
            except KeyError:
                try:
                    link = movie_link.find('a')['href']
                except TypeError:
                    pass
            if link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_text=title,
                )
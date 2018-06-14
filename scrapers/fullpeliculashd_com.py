# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FullpeliculashdCom(SimpleScraperBase):
    BASE_URL = 'https://www.fullpeliculashd.com'
    OTHERS_URLS = ['http://www.fullpeliculashd.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u"No se ha encontrado resultado a su búsqueda"

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/buscar/?q={}&page={}'.format(search_term, start)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found = False

        for result in soup.select('h2.titpeli a'):
            found = True
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.titbkcnt').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.find('div', 'tab_container').find_all('div', id=re.compile('ms\d+')):
            iframe = link.find('iframe')
            if iframe and iframe.has_attr('src'):
                src = iframe['src']
                if src.find('http') == -1:
                    src = 'http:' + src

                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=src,
                                         link_title=title
                                         )

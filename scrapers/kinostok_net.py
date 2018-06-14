# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class KinoStokNet(SimpleScraperBase):
    BASE_URL = 'http://www.kinostok.net'
    LONG_SEARCH_RESULT_KEYWORD = 'R'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Не найдено материалов доступных для просмотра'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/load/',
                data={
                    'query': search_term,
                    'sfSbm': u'Найти',
                    'a': '2',
                })
        )

    def _parse_search_result_page(self, soup):
        # 1994 styling.  Look for a div with the id="entryIDXXX".
        found = False
        for result in soup.findAll(
                'div', attrs={'id': re.compile('^entryID')}):
            # First link.
            link = result.find('a')
            # First linked image...
            found = True
            image = result.select('a img')[0]['src']
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image
            )

        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # All looks like simple iframes.
        for iframe in soup.select('table.eBlock iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     )

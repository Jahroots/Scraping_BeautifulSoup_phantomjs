# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class OnlainFilmUcozUa(SimpleScraperBase):
    BASE_URL = 'http://onlainfilm.me'
    OTHER_URLS = ['http://onlainfilm.ucoz.ua']
    LONG_SEARCH_RESULT_KEYWORD = u'папа'
    SINGLE_RESULTS_PAGE = True

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
        return u'Не найдено материалов'

    def _fetch_next_button(self, soup):
        # XXX
        # Next page is odd, and only appears on an invalid search, being
        # one with too short a name?  Less than 4 characters I think.
        # WHen it does appear, it posts to itself with no search params
        # so looks like a session based repeat
        return None

    def search(self, search_term, media_type, **extra):
        self.__opened_pages = set()
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/load/',
                data={
                    'query': search_term,
                    'a': 2,
                }
            )
        )

    def _parse_search_result_page(self, soup):
        for result in soup.findAll('div',
                                   attrs={'id': re.compile('^entryID\d+')}):
            # Take the first
            link = result.find('a')
            # And the first linked image.
            image = result.select('a img')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image['src']
            )

    def _parse_parse_page(self, soup):
        # Atleast this bits easy, eh?
        for iframe in soup.select('td.eText iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + iframe['src'] if iframe['src'].startswith('//') else  iframe['src'],
                                     )

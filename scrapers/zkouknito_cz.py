# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin
import re
import json


class ZkouknitoCz(SimpleScraperBase):
    BASE_URL = 'http://www.zkouknito.cz'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_AGENT_MOBILE = False

    def _fetch_no_results_text(self):
        return u'Hledanému výrazu nic neodpovídá.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/hledej-videa?string=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        if link:
            return self.BASE_URL+link['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('.preview h2 a'):
             self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        raw = re.search('"sd":{"src":.*\"', soup.text).group(0).split('"sd":')[1] + '}'
        obj = json.loads(raw)
        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                 link_url=obj['src'])

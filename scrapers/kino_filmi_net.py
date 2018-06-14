# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class KinoFilmiNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kino-filmi.net'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов. Попробуйте изменить или сократить Ваш запрос'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))


    def _parse_search_result_page(self, soup):
        for link in soup.select('h3.title a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.title').text
        for link in soup.select('div#dle-content iframe'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url= link['src'],
                                     link_title=title,
                                     )
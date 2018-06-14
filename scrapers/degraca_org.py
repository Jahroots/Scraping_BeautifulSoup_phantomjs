# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Degraca(SimpleScraperBase):
    BASE_URL = 'https://torrentfilmes.net'
    OTHER_URLS = ['http://www.degraca.org', 'http://degracaemaisgostoso.org', ]
    #LONG_SEARCH_RESULT_KEYWORD = 'The Final Master'
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'XWIS0V6L'

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

    def _parse_search_result_page(self, soup):
        found = 0
        for link in soup.select('div.listagem div.item a'):
            found = 1
            self.submit_search_result(
                link_title=link.title,
                link_url=link.href
            )
        if not found:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Proxima »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.title.text[11:]
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('div[class="bt-down azul"] a') + soup.select('div[class="bt-down verde"] a'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

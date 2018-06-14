# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Megaflick(SimpleScraperBase):
    BASE_URL = 'http://megaflick.biz'
    OTHER_URLS = []

    def setup(self):
        raise NotImplementedError('Deprecated, website just contains ads.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('------------------------')
        return  next['href'] if next else None

    def _parse_search_result_page(self, soup):

        for link in soup.select('.entry-title.panel-title a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def _parse_parse_page(self, soup):
        title = soup.title.text.split('|')[0].strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for dl in soup.select('.entry-content a'):
            if not dl.parent.name == 'li':
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=dl.text,
                                         link_text=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

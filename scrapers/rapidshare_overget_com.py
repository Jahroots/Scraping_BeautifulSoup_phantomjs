# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Overget(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://rapidshare.overget.com'

    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):

        raise NotImplementedError('Site no longer available.')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 1, tv 5'
        # self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def _parse_search_result_page(self, soup):
        for link in soup.select('.title a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('.title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.summary a'):
            if not link.href.startswith(self.BASE_URL) and link.href.startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for code_box in soup.select('.quote'):
            text = str(code_box).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(text):
                if url.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )

        for link in soup.select('#dle-content center a b'):
            link = link.parent.href
            if not link.startswith(self.BASE_URL) and link.startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
        #
        # for box in soup.select('.summary'):
        #     for url in self.util.find_urls_in_text(box.text):
                #         self.submit_parse_result(
        #             link_url=url,
        #             link_title=title,
        #             series_season=series_season,
        #             series_episode=series_episode,
        #         )
# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Kinodrom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinodrom.ws'
    OTHER_URLS = ['http://kinodrom.net']
    LONG_SEARCH_RESULT_KEYWORD = 'жизнь'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 0, tv 0'
        self.encode_search_term_to = 'cp1251'
        # self.showposts = 0
        raise NotImplementedError

    def _parse_search_result_page(self, soup):
        for link in soup.select('.title h1 a'):
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        try:
            title = soup.select_one('.title > h1').text
            # series_season, series_episode = self.util.extract_season_episode(title)

            for lnk in soup.select('.quote a'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=lnk.href,
                                         link_title=title,
                                         # series_season=season,
                                         # series_episode=episode,
                                         )
            for box in soup.select('.quote'):
                for url in self.util.find_urls_in_text(box.text):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             # series_season=series_season,
                                             # series_episode=series_episode,
                                             )

        except:
            pass

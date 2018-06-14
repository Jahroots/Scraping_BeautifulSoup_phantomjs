# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, SimpleGoogleScraperBase


class BoardsNet(SimpleGoogleScraperBase):
    BASE_URL = 'https://boards.net'
    OTHER_URLS = ['http://boards.net' ]
    LONG_SEARCH_RESULT_KEYWORD = 'dvdrip'
    NO_RESULTS_KEYWORD = 'hhhdddnnnHFEJRYFG746TU43GT'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Default BackEnd 404')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          re.compile('.*\.boards.net'))
        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          re.compile('.*\.boards.net'))

    def get(self, url, **kwargs):
        return super(BoardsNet, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):

        title = soup.title.text.strip()
        season, episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('.message'):
            for url in self.util.find_urls_in_text(link.text):
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

        for link in soup.select('.message a'):
            if link.startswith_http and 'boards.net' not in link.href:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

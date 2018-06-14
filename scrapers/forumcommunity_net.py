# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, DuckDuckGo



class ForumCommunity(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.forumcommunity.net'
    OTHER_URLS = ['http://revelation.forumcommunity.net', ]
    LONG_SEARCH_RESULT_KEYWORD = 'dvdrip'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website nor Relevant Anymore.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          re.compile('.*\.forumcommunity.net'))
        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          re.compile('.*\.forumcommunity.net'))



    def get(self, url, **kwargs):
        return super(ForumCommunity, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):

        title = soup.title.text.strip().split(' - ')[0]
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.code'):
            for url in self.util.find_urls_in_text(link.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

        for link in soup.select('.color a'):
            if link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

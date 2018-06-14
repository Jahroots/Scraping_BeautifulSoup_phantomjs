# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, DuckDuckGo


class VidtoMe(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://vidto.me'
    LONG_SEARCH_RESULT_KEYWORD = 'n'
    SINGLE_RESULTS_PAGE = True
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    PARSE_RESULTS_FROM_SEARCH = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(VidtoMe, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):
        url = soup._url
        if 'embed' in url:
            title = self.util.get_page_title(self.get_soup(url.replace('embed-', '').replace('.html', ''))).strip()
            self.submit_parse_result(index_page_title=title,
                                             link_url=url)

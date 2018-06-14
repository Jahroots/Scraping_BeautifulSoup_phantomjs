# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, DuckDuckGo


class UlozTo(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'https://www.uloz.to'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'zce'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def parse(self, parse_url, **extra):
        if '?q=' not in parse_url:
            title = self.util.get_page_title(self.get_soup(parse_url)).strip()
            self.submit_parse_result(index_page_title=title,
                                     link_url=parse_url)

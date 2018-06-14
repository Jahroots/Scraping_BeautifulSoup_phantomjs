# -*- coding: utf-8 -*-
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import DuckDuckGo, SimpleScraperBase


class ShareOnlineBiz(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.share-online.biz/'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          self.BASE_URL)

    def _parse_parse_page(self, soup):
        block = None
        try:
            block = soup.find('table', id='dl_package')
        except AttributeError:
            pass
        if block:
            title = soup.find('div', id='download').find('script', text=re.compile('var fn="')).text.split('var fn="')\
                [-1].split('";')[0]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=soup._url,
                                     link_title=title,
                                     )
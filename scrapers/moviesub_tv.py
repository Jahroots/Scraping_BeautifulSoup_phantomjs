# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from moviesub_org import MoviesubOrg

class MoviesubTv(MoviesubOrg):
    BASE_URL = 'https://moviesub.is'
    OTHERS_URLS = ['http://moviesub.tv']
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self._request_connect_timeout = 60
        self._request_response_timeout = 120


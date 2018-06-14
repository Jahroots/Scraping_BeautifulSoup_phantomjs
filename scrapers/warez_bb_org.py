#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import PHPBBSimpleScraperBase


class WarezBbOrgFilm(PHPBBSimpleScraperBase):

    BASE_URL = 'https://www.warez-bb.org'

    # Note - fakenamegenerator domains are banned.
    USERNAME = 'Theirach1957'
    PASSWORD = 'sikeChae0Du'
    EMAIL = 'warezbb@myspoonfedmonkey.com'

    FORUMS = 4

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

class WarezBbOrgTV(WarezBbOrgFilm):

    FORUMS = 57

    def setup(self):
        raise NotImplementedError('Duplicate of WarezBbOrgFilm')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)


# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, SimpleGoogleScraperBase
import re

class FlixTapuzCoIl(SimpleGoogleScraperBase):
    BASE_URL = 'http://www.tapuz.co.il'
    OTHER_URLS = ['http://flix.tapuz.co.il']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'heb'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def parse(self, parse_url, **extra):
        content = self.get(parse_url).content
        soup = self.make_soup(content)
        index_page_title = self.util.get_page_title(soup)

        for url in re.findall('<source src="(.*?)"', content):

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url
            )

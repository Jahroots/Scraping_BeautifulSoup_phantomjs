# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import time

class VidmateMobi(SimpleScraperBase):
    BASE_URL = 'http://www.vidmate.com'
    OTHER_URLS = ['http://www.vidmate.mobi']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ]
    SINGLE_RESULTS_PAGE = True

    # This scraper used a whole bunch of decryption in it's

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/featured-search/{}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def _fetch_no_results_text(self):
        return u'Dear, no related data'

    def _parse_search_result_page(self, soup):
        results = soup.select('#search a.link')
        for result in results:
            self.submit_search_result(
                link_url = result.href,
                link_title = result.title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1')
        if title:
            title = title.text
        files = soup.select('ul.resources-list li.resources-item a')
        for file in files:
            self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                     link_title=title,
                                     link_url=file.href
                                     )




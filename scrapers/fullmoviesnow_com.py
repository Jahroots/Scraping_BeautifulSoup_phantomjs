# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FullMoviesNow(SimpleScraperBase):
    BASE_URL = 'https://popnewslive.com'
    OTHER_URLS = ['https://fullmoviesnow.com']

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u"Nothing Found"

    def _fetch_next_button(self, soup):
        return

    def _parse_search_result_page(self, soup):
        for result in soup.select('article h2.entry-title a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup)

# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PeeLink2Org(SimpleScraperBase):
    BASE_URL = 'http://www.peelink.tv'
    OTHER_URLS = [
        'http://www.peelink2.net',
        'http://www.peelink2.org',
    ]
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = '3wagc0E4'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'spa'
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_no_results_text(self):
        return 'No se ha encontrado'

    def _fetch_next_button(self, soup):
        # No pagination...
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.contenti'):

            url = result.select_one('a')
            if url:
                self.submit_search_result(
                    link_url=url.href,
                    link_title=url.text,
                    image=self.util.find_image_src_or_none(result, 'img')
                )

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup, 'div.post-body iframe')

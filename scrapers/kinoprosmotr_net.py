# coding=utf-8

from sandcrawler.scraper import FlashVarsMixin
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class KinoProSmotrNet(OpenSearchMixin, SimpleScraperBase, FlashVarsMixin):
    BASE_URL = 'http://kinoprosmotr.co'
    OTHERS_URLS = ['http://kinoprosmotr.xyz','http://kinoprosmotr.cc', 'http://kinoprosmotr.club', 'http://kinoprosmotr.tv']
    TRELLO_ID = 'LLmYdqy9'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.search_term_encoding = 'windows-1251'
        self._request_connect_timeout = 300
        self._request_response_timeout = 400

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _parse_search_result_page(self, soup):
        results = soup.select('div.search_item div.search_item_inner h3 a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('div.search_item'):
            # First link in the heading
            link = result.select('div.search_item_inner h3 a')[0]
            # first image in the content is a link to the big image.
            image = result.select('div.search_item_prev img')[0]['src']
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.BASE_URL + image,
            )

    def _parse_parse_page(self, soup):
        title = soup.title.text.split(u' смотреть онлайн')[0]

        for obj in soup.findAll('param', attrs={'name': 'flashvars'}):
            self._parse_flashvars_from_query_string(obj['value'])

        for iframe in soup.select('.full_movie iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe['src'],
                )

        for script in soup.select('div.full_movie_top div.full_movie_trailer script'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=script['src'],
            )

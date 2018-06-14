# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class StreamizFilms(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://ww1.streamiz-filmze.com'
    OTHER_URLS = [
        'http://streamiz-filmze.tv',
        'http://streamiz.voirfilmze.com',
        "https://streamiz-films.com",
        "http://streamiz-films.com",
        "http://streamiz.voirfilmze.com"
    ]
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    PAGE = 1
    COUNT = 0
    SEARCH_TERM = ''
    TRELLO_ID = '2zvFGfVt'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 25
        self._request_connect_timeout = 600
        self._request_response_timeout = 600

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="mov-short incat"] a')
        self.COUNT += len(results)
        if not results:
            self.submit_search_no_results()
        for result in results:
            self.submit_search_result(link_title=result.img.get('title'),
                                      link_url=result.get('href'))


    def _parse_parse_page(self, soup):
        title = soup.select_one('.movie-title h1').text

        self._parse_iframes(soup, link_title=title)

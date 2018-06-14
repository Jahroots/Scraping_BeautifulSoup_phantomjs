# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase,  SimpleGoogleScraperBase


class IsraboxCo(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'https://www.israbox.pro'
    OTHER_URLS = ['https://www.israbox.com', 'https://www.israbox.live', 'https://www.israbox.cc', 'https://www.israbox.io', 'https://www.israbox.vip', 'https://www.israbox.one',
                  'https://www.israbox.plus', 'https://www.israbox.media', 'https://music.israbox.net',
                  'https://www.israbox.pw', 'https://www.israbox.one']
    SINGLE_RESULTS_PAGE = True

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    USER_AGENT_MOBILE = False
    TRELLO_ID = 'Lu9MeNNu'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.bunch_size = 40

        self.showposts = 0
        self._request_response_timeout = 300
        self._request_connect_timeout = 300

    def _fetch_no_results_text(self):
        return None

    def _parse_parse_page(self, soup):
        for link in soup.select('div.quote a'):
            index_page_title = self.util.get_page_title(soup)
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=link.href)

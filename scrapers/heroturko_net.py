# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Heroturko(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = "http://www.heroturko.net"

    # SINGLE_RESULTS_PAGE = True
    # LONG_SEARCH_RESULT_KEYWORD = 'война'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 531, tv 527'
        # self.encode_search_term_to = 'cp1251'
        self.showposts = 1

    def _parse_search_result_page(self, soup):
        for result in soup.select(".storytitle a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _parse_parse_page(self, soup):

        for code_box in soup.select('.quote'):
            text = str(code_box).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(text):
                if url.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             )

        for url in soup.select('.quote a'):
            if url.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url.href,
                                         link_title=url.text,
                                         )

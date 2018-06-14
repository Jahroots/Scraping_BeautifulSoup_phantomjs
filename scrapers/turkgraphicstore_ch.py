# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class TurkGraphicStore(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://gfxtra.ch'
    OTHERS_URLS = ["http://www.turkgraphicstore.ch"]

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        self.TERM = search_term
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
       return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[style] a[href*="'+ self.TERM +'"]')
        if not results:
            self.submit_search_no_results()

        for item in results:
            self.submit_search_result(
                link_url=item['href'],
                link_title=item.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2').text
        results = self.util.find_urls_in_text(soup.select_one('div.quote').text.replace('https', 'http'))
        for result in results:
            links = result.split('http')
            for link in links:
                if link and len(link) > 1:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url='http' + link,
                                             link_title = title,
                                             )


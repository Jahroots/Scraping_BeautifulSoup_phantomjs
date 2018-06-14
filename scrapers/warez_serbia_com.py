# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class WarezSerbia(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = "http://warez-serbia.com"
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 2, tv 20'

    def _parse_search_result_page(self, soup):
        results = soup.select(".box-socket h2 a")
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('#news-title').text

        for link in soup.select('.main-container.center.story div pre code'):
            for _link in link.text.split('\n'):
                if 'imdb.com' not in _link:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=_link,
                                             link_text=title,
                                             # series_season=series_season,
                                             # series_episode=series_episode,
                                             )

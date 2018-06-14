# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class KanKanDotCom(SimpleScraperBase):
    LONG_SEARCH_RESULT_KEYWORD = 'rock 2015'
    BASE_URL = 'http://www.kankan.com/'
    PAGE = 1

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        # Note uses chinese proxy.

        self.search_term_language = "zho"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, 'http://kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://video.kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://data.movie.kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://vod.kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://yule.kankan.com')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://search.kankan.com')



    def _fetch_search_url(self, search_term, media_type):
        self.current_search = "http://search.kankan.com/search.php?keyword=" + self.util.quote(search_term)
        return self.current_search

    def _fetch_no_results_text(self):
        return u'很抱歉'
    def _fetch_next_button(self, soup):
        self.PAGE += 1
        return self.current_search + "&page=" + str(self.PAGE)

    def search(self, search_term, media_type, **extra):
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        if self._fetch_no_results_text() in unicode(soup):
            return self.submit_search_no_results()

        self.submit_search_result(
                link_url = self.current_search + "&page=" + str(self.PAGE),
                link_title = self.util.get_page_title(soup)
            )

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        index_page_title = self.util.get_page_title(soup)
        videos = soup.select('div.playbtn_play a')

        if not videos:
            videos = soup.select('ul[class="imglist imglist_150x85"] a.pic')

        for video in videos:
            self.submit_parse_result(
                    index_page_title = index_page_title,
                    link_url= video['href'],
            )

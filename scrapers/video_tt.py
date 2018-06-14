# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Video_tt(SimpleScraperBase):
    BASE_URL = "http://video.tt"

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'maldives'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        raise NotImplementedError('The website is not reachable')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/video_search.php?search=' + search_term

    def _fetch_no_results_text(self):
        return 'did not match any videos'

    def _parse_search_result_page(self, soup):
       # self.log.debug(soup)
        results = soup.select('.video_title > h2 > a')
        for lnk in results:
            self.submit_search_result(link_url=self.BASE_URL + lnk.href,
                                      link_title=lnk.text)

    def _fetch_next_button(self, soup):
        nxt = soup.find('a', text='›')
        if nxt:
            return nxt.href

    def _parse_parse_page(self, soup):
        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                 link_url=self.BASE_URL + '/watch_video.php?v=' + soup._url[22:]
                                 )

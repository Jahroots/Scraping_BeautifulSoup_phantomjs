# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class SixtyTwoY(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.62y.net'
    HAS_RECORDS = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
         self.HAS_RECORDS = False
         super(self.__class__, self).search(search_term, media_type, **extra)
    #     soup = self.post_soup(self.BASE_URL, data=dict(do='search', subaction='search', story=search_term))
    #     self._parse_search_results(soup)

    # def _fetch_next_button(self, soup):
    #     next = soup.select_one('#nextlink')
    #     self.log.debug('----------------')
    #     return next.href if next else None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)


    def _fetch_no_results_text(self):
        return None

    def _parse_search_result_page(self, soup):

        results = soup.select(".btl a")
        if (not results or len(results) == 0) and not self.HAS_RECORDS:
            return self.submit_search_no_results()

        self.HAS_RECORDS = True

        for result in results:
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))


    def _parse_parse_page(self, soup):

        series_season =  series_episode = None
        title = soup.select_one('h3.btl')
        if not title:
            title = soup.select_one('h1.title')

        if title:
            title = title.text
            series_season, series_episode = self.util.extract_season_episode(title)

        for url in soup.select('.maincont a'):
            if url.startswith_http :
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        code_box = soup.select_one('.maincont')
        if code_box:
            for url in self.util.find_urls_in_text(unicode(code_box)):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )


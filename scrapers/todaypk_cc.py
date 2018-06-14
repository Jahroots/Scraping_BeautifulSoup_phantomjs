#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TodaypkCC(SimpleScraperBase):

    BASE_URL = 'https://todaypk.ch'
    OTHER_URLS = ['https://todaypk.ms', 'https://todaypk.se', 'https://todaypk.at', 'https://www.todaypk.se','https://www.todaypk.ag', 'https://todaypk.li','http://todaypk.la', 'http://todaypk.is', 'http://todaypk.cc', 'http://todaypk.com', 'http://todaypk.cz']
    TRELLO_ID = '8lHvhGqr'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(TodaypkCC, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return "No content available"

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/page/{}/?s={}'.format(start, search_term)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        rslts = soup.select('#uwee div.fitem')
        if not rslts:
            self.submit_search_no_results()
        for result in rslts:
            result = result.select_one('a')
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.years span.a a'):
            url = link['href']
            link_title = link['title']
            if '/watchfree.php' in url or 'magnet' in url:
                continue
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url,
                                     link_title=link_title,
                                     )

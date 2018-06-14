#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Rapid4MeCom(SimpleScraperBase):

    BASE_URL = 'http://rapid4me.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'were found for the'

    @property
    def current_page(self):
        if not hasattr(self, '_current_page'):
            self._current_page = 1
        return self._current_page

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?file_type=1&p=%s&q=%s' % \
            (self.current_page, self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        # No next button - keep a stateful page.
        link = soup.find('a', 'pagenumber',
            text=' %s ' % (self.current_page + 1))
        if link:
            self._current_page += 1
            return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('tr.search_item td.pull-right a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip(),
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('p.fade a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     )

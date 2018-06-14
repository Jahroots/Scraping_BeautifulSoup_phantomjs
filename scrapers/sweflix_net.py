# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SweFlixNet(SimpleScraperBase):
    BASE_URL = 'http://www.sweflix.ws'

    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        # Even Google thinks it's English, though...
        self.search_term_language = "swe"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'No content available'

    def _fetch_next_button(self, soup):
        curr_butt = soup.select_one('.current')
        if curr_butt and curr_butt.parent.find_next_sibling() and curr_butt.parent.find_next_sibling().name == 'li':
            self.log.debug('---------------------')
            return soup.select('.page.larger')[-1].href

    def _parse_search_result_page(self, soup):
        for result in soup.select('.item .boxinfo a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.select_one('.tt').text,
            )

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup, css_selector='iframe')


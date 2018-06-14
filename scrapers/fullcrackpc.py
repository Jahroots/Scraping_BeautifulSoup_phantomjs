# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import requests


class FullCrackPc(SimpleScraperBase):
    BASE_URL = 'http://fullcrackpc.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tha'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search terms'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}&ixsl=1'.format(self.util.quote(search_term))

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[500], **kwargs)

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        response = requests.get(self._fetch_search_url(search_term, media_type)).text
        soup = self.make_soup(response)
        self._parse_search_result_page(soup)
    def _parse_search_result_page(self, soup):
        blocks = soup.select('article header h2.entry-title')
        if not blocks or len(blocks) == 0:
            return self.submit_search_no_results()

        for block in blocks:
            link = block.select_one('a')['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
                image=self.util.find_image_src_or_none(block, 'img'),
            )

    def _parse_parse_page(self, soup):
            for link in soup.select('li#ert_pane1-0 pre a')+soup.select('li#ert_pane1-0 a'):
                if self.BASE_URL not in link.text:
                    index_page_title = self.util.get_page_title(soup)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text
                    )
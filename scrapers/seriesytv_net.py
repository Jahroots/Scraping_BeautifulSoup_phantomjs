# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re

class SeriesytvNet(SimpleScraperBase):
    BASE_URL = 'http://seriesytv.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403], verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/rj452.php'

    def _fetch_no_results_text(self):
        return u'NO SE A ENCONTRADO RESULTADOS'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {'q' : search_term})
        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('li.q a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            soup = self.get_soup(link.href)
            links = soup.select('#listado li a')
            for link in links:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_result_page(self.get_soup(next_button_link))



    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        m = re.search(r'(<iframe src=).*(\.html)', soup.text)
        if m:
            soup = self.make_soup(m.group(0))

            for link in soup.select('iframe'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re
class WatchinItNu(SimpleScraperBase):
    BASE_URL = 'http://watchin-it.nu'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?movieSort=search&search=1'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=re.compile('next'))

        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {'search' : search_term, 'submit' : 'Go'})
        self._parse_search_result_page(soup)

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            self._parse_search_result_page(self.get_soup(next_button))

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.products li a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url= self.BASE_URL + '/' + link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('center a.image2'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
            )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TheDareTube(SimpleScraperBase):
    BASE_URL = 'http://www.thedaretube.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, your search did not yield any results'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return self.BASE_URL + "/"+ link['href'] if link else None

    def _fetch_search_url(self, search_term, media_type, start=None):
        return self.BASE_URL + '/search.php?keywords=' + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul[class="videolist biglist"] li a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[itemprop="name"]').text.strip()

        for link in soup.select('#video_primary source'):
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title
            )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase

class VeoSeriesOnline(SimpleScraperBase):
    BASE_URL = 'http://veoseriesonline.com'

    def setup(self):
        raise NotImplementedError('Website Not Available')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)



    def get(self, url, **kwargs):
        return super(VeoSeriesOnline, self).get(
            url, allowed_errors_codes=[403], **kwargs)

    def _fetch_no_results_text(self):
        return 'Lo sentimos, no podemos encontrar resultados'

    def _fetch_next_button(self, soup):
        links = soup.select('div.pagenavi a')

        if not links or len(links) == 0:
            return None

        return links[-1]['href'] if links[-1] else None

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        soup = self.get_soup(search_url)
        self._parse_search_result_page(soup)

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_result_page(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        results = soup.select('ul[class="search-results-content infinite"] a[title]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            if not 'page' in result['href']:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result['title']
                )

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=%s' % self.util.quote(search_term)

    def _parse_parse_page(self, soup):
        #Check img for real video url
        for link in soup.select('table[class="table table-hover"] img[src*="http://www.google.com/s2/favicons?"]'):
            link_href = link['src'].split('=')[1]
            link_title = link['title']

            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url = link_href,
                link_title = link_title
            )

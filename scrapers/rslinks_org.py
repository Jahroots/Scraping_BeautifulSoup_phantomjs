# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class RSLinksOrg(SimpleScraperBase):
    BASE_URL = 'http://rslinks.org'
    OTHER_URLS = ['http://www.rslinks.org', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Your search yielded no results'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'next')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ol.search-results div h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.field-items a[target="_blank"]'):
            if not link['href'].startswith(self.BASE_URL):
                self.submit_parse_result (
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link['href'],
                    link_title=link.text,
                )

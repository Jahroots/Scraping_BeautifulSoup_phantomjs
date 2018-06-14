# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class ExDown(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.extreme-down.im'
    OTHER_URL = ['https://www.extreme-down.pro', 'https://www.extreme-down.one', 'https://www.extreme-down.in']


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u"La recherche n'a retourné aucun résultat"

    def _parse_search_result_page(self, soup):
        results = soup.select('a[class="top-last thumbnails"]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                image = self.util.find_image_src_or_none(result, 'img')
            )


    def _parse_parse_page(self, soup):
        for link in soup.select('a[href*="ed-protect"]'):
            self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link['href'],
                    link_title=link.text
                )

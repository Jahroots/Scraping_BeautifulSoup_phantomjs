# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase, OpenSearchMixin
from sandcrawler.scraper import SimpleScraperBase


class FilmeSeriale2016(SimpleScraperBase):
    BASE_URL = 'http://filmeseriale2016.com'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rum'

        # raise NotImplementedError("The website is Blocked")
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'nu a returnat niciun rezultat'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return 'http:'+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        if not soup.select('div.eTitle') and len(soup.select('div.eTitle')) == 0:
            return self.submit_search_no_results()
        results = soup.select('div.eTitle')

        for result in results:
            link = result.select_one('a')
            self.submit_search_result(
                link_url= link['href'],
                link_title= link.text,
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.eTitle').text.strip()

        for link in soup.select('iframe[src*="https"]'):
            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url = link['src'],
                link_title = title
            )
# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PuxandoLegalOrg(SimpleScraperBase):
    BASE_URL = 'https://baixar.link'
    OTHER_URLS = ['http://www.puxandolegal.org', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'por'
        raise NotImplementedError('The website is empty and does not have relevant data')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'There has been an error.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next ›')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.home_page div.post h2.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.post-single-content a[rel="nofollow"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_title=link.text,
                )

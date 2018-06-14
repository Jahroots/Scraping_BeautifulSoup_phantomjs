# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PublizHare(SimpleScraperBase):
    BASE_URL = 'http://www.publizhare.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search terms.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Next Page »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.article-wrapper h2.entry-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip(),
            )

    def _parse_parse_page(self, soup):
        image = self.util.find_image_src_or_none(soup, 'div.entry-content img')
        for link in soup.select('div.entry-content a'):
            if link.get('href') and \
                link['href'].startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         image=image,
                                         )

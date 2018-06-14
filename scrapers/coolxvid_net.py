# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class CoolXVidNet(SimpleScraperBase):
    BASE_URL = 'http://www.coolxvid.net'

    LONG_SEARCH_RESULT_KEYWORD = 'Test 1'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No posts were found.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'nextpostslink')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post div.post-title h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        image = self.util.find_image_src_or_none(soup, 'div.content img.aligncenter')
        for link in soup.select('div.post div.content a'):
            if not link['href'].startswith(self.BASE_URL):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=link.text,
                                         image=image,
                                         ),

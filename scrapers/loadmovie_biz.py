# -*- coding: utf-8 -*-
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class LoadMovieBiz(SimpleScraperBase):
    BASE_URL = 'http://loadmovie.biz'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'nextpostslink')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.blog-item div.post-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            time.sleep(1)  # probably rate limiting enabled @ the host

    @cacheable()
    def __follow_redirect(self, url):
        return self.get_redirect_location(url)

    def _parse_parse_page(self, soup):
        # First image on the content.
        image = self.util.find_image_src_or_none(soup,
                                                 'div.post_content_wrapper img')
        for link in soup.select('div.post_content_wrapper a'):
            if link['href'].startswith('/g/'):
                dest_url = self.__follow_redirect(self.BASE_URL + link['href'])
                if dest_url:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=dest_url,
                                             link_title=link.text
                                             )

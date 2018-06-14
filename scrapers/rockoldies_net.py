# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class RockOldiesNet(SimpleScraperBase):
    BASE_URL = 'http://rockoldies.net'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'deu'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        def _fetch_search_url(self, search_term, media_type):
            return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'No posts found'

    def _fetch_next_button(self, soup):
        link = soup.select_one('li[class="next right"] a')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):

        results = soup.select('div.main h2[class="post-title entry-title"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            result = result.select_one('a')

            if result and result['href']:
                self.submit_search_result(
                            link_url=result.href,
                            link_title=result.text,
                )


    def _parse_parse_page(self, soup):
        image = self.util.find_image_src_or_none(soup, 'div.post_body img')
        for link in soup.select('div.post_body a'):
            if link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=link.text,
                                         image=image
                                         )

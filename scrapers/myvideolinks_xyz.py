# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MyVideoLinksXyz(SimpleScraperBase):
    BASE_URL =  'http://go.myvideolinks.net'
    OTHER_URLS = ['http://dl.newmyvideolink.xyz', 'http://newmyvideolink.xyz', 'https://myvideolinks.tk', 'http://go.newmyvideolink.xyz', 'http://download.myvideolinks.xyz', 'http://newmyvideolink.xyz']
    page = 1
    flag = False
    TRELLO_ID = 'p9wMbB0J'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for site in [self.BASE_URL]+self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _fetch_no_results_text(self):
        return 'Cannot find what you are looking for'

    def _fetch_search_url(self, search_term, media_type):
        self.search_term = search_term
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_next_button(self, soup):
        next = soup.select_one('#post-navigator').find('a', text=u'›')
        if next:
            return next.href
        else:
            return None

    def search(self, search_term, media_type, **extra):
        self.page = 1
        self.flag = False
        super(self.__class__, self).search(search_term, media_type)

    def _parse_search_result_page(self, soup):
        if "Sorry, we can't find the search keyword you're looking for" in soup.text:
            self.flag = True
            return self.submit_search_no_results()

        results = soup.select('#post-entry article h2.post-title')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image = self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_parse_page(self, soup):
        # Just links in the post content - includes an imdb and youtubue
        # sometimes.
        for link in soup.select('div.entry-content iframe'):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link['src'],
                                         link_title=link.text,
                                         )

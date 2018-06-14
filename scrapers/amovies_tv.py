# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AMoviesTV(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinomoov.net/'
    OTHER_URLS = ['http://amovies.tv/']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        raise NotImplementedError('redirect to http://kinomoov.net -> see appropriate scraper')

        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term):
        return self.BASE_URL

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту'

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('div#dle-content > li'):
            found = 1
            link = result.select_one('div.post_name a')
            image = self.util.find_image_src_or_none(soup, 'div.post_prev_img img')
            image = image and self.BASE_URL + image or None
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image,
            )
        if not found:
            self.submit_search_no_results()

    def parse(self, page_url, **extra):
        # Videos directly embedded in iframes!
        for soup in self.soup_each([page_url, ]):
            for iframe in soup.select('iframe'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=iframe['src']
                                         )

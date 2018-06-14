# coding=utf-8
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Jarochos(SimpleScraperBase):
    BASE_URL = 'https://jarochos.net'
    OTHER_URLS = ["http://jarochos.net"]
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)


    def _parse_search_result_page(self, soup):
        for link in soup.select('div.box_a a.titleContent'):
            self.submit_search_result(
                link_url=u'{}/{}'.format(self.BASE_URL, link.href),
                link_title=link.text,
            )

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/?tag={}&o=p'.format(
            self.BASE_URL,
            search_term.decode('utf-8'),
        )

    def _fetch_no_results_text(self):
        return 'There are no articles to display'

    def _fetch_next_button(self, soup):
        link = soup.select_one('div.moreArticles a')
        if link:
            return u'{}/{}'.format(self.BASE_URL, link.href)
        return None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1')
        if title and title.text:
            title = title.text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('.externalLink'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_title=title,
                link_url=link.href
            )

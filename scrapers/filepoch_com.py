# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Filepoch(SimpleScraperBase):
    BASE_URL = 'http://filepoch.com'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?x=1&q=' + search_term

    def _fetch_no_results_text(self):
        return '<strong>1 - 0</strong>'

    def _get_search_results(self, search_term, page):
        return self.post_soup(self.BASE_URL + '/?q=' + search_term, data=dict(
            x=1, q=search_term, file_shares='', files_type=0, files_size=0, p=page))

    def _fetch_next_button(self, soup):
        pagenumber = soup.select_one('.pagenumber')
        if not pagenumber:
            return None
        next_sibling = pagenumber.find_next_sibling()
        if not next_sibling or next_sibling.name != 'a':
            return None
        return self.BASE_URL + next_sibling.href

    def _parse_search_result_page(self, soup):
        found = False

        for link in soup.select('.search_item a.font120'):
            found = True
            self.submit_search_result(
                link_title=link.text,
                link_url=self.BASE_URL + link.href
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.title.text.split(' - ')[0]
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.results-table.width100 td a'):

            if link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

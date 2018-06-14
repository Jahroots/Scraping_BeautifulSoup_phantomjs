# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DownloadHub(SimpleScraperBase):
    BASE_URL = 'https://downloadhub.ws'
    OTHER_URLS = ['https://downloadhub.org', 'https://downloadhub.in', 'http://downloadhub.in', 'http://downloadhub.net']

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = '5wAimEPo'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

            # self.long_parse = True

    def _fetch_no_results_text(self):
        return "No result TV Series or Episodes for"

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('-----------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.thumb a'):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.href)
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('h1').text
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('main.page-body a'):
            # Only external links.
            if not link.href.startswith('http'):
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link.href,
                link_title=title,
                series_season=season,
                series_episode=episode
            )

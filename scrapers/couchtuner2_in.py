# -*- coding: utf-8 -*-
import re
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException

class CouchTuner2In(SimpleScraperBase):
    BASE_URL = 'http://couch-tuner2.in'
    OTHER_URLS = []

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'afr'
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):

        search_soup = self.get_soup(
            '{}/s?s={}'.format(
                self.BASE_URL,
                self.util.quote(search_term)
            )
        )

        results = search_soup.select('div.arch-post h1 a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            series_soup = self.get_soup(link.href)
            for episode_link in series_soup.select('div.episode-list li a'):
                self.submit_search_result(
                    link_url=episode_link.href,
                    link_title=episode_link.text,
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for container in soup.select('div.iframe-container b'):
            for link in self.util.find_urls_in_text(str(container)):
                self.submit_parse_result(
                    link_url=link,
                    index_page_title=index_page_title
                )
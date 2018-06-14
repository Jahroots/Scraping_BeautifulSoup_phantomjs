# -*- coding: utf-8 -*-

import time
import random

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CacheableParseResultsMixin, \
    ScraperFetchException
from sandcrawler.scraper.caching import cacheable


class Vidics(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'https://www.vidics.to'
    OTHER_URLS = ['http://www.vidics.ch']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        self.search_url = self.BASE_URL + '/Category-{cat}/Genre-Any/Letter-Any/ByPopularity/{page}/Search-{term}.htm'
        self.search_page_no = 1
        self.media_type = media_type
        self.search_term = search_term
        return self.search_url.format(
            cat='FilmsAndTV' if media_type == self.MEDIA_TYPE_FILM else 'TvShows',
            term=search_term,
            page=self.search_page_no
            )

    def _fetch_no_results_text(self):
        return 'No results'

    def _fetch_next_button(self, soup):
        button = soup.select_one('button#searchShowMore')
        if button:
            return u'{}{}'.format(self.BASE_URL, button.href)
        return None

    @cacheable()
    def get_search_results(self, url):
        series_soup = self.get_soup(url)
        results = []
        for episode_link in series_soup.select('div.season a.episode'):
            results.append(dict(
                link_url=self.BASE_URL + episode_link['href'],
                link_title=episode_link.get('title').encode('utf-8', 'ignore'),
            ))
        return results

    def _parse_search_result_page(self, soup):
        total = soup.select_one('#searchResults h3')
        # NOTE - often this site just returns
        # ERROR 1: The current page is bigger then the last page. Last page is in the code of this error.
        # Which is, well, wrong.
        if total and total.text:
            results = soup.select('.searchResult div.poster a')
            if not results or len(results) == 0:
                # Search no results on subsequent pages from the first.
                if '/1/' in soup._url:
                    self.submit_search_no_results()
                # But always bail.
                return

            for link in results:

                # If it's a season, fetch it then submit each episode
                # as a parse result.
                if 'Serie' in link['href']:
                    for result in self.get_search_results(self.BASE_URL + link['href']):
                        self.submit_search_result(
                            **result
                        )

                else:
                    self.submit_search_result(
                        link_url=self.BASE_URL + link['href'],
                        link_title=link.get('title'),
                    )
        elif '/1/' in soup._url:
            if soup.find('h5', text='No results'):
                self.submit_search_no_results()

    # These are pretty static - give it a month.
    @cacheable(60 * 60 * 24 * 30)
    def _follow_redirect(self, url):
        # Try again in a little bit - cheaper than retrying the whole task
        soup = self.get_soup(url)
        link = soup.select_one('div.movie_link1 a')
        return link.href

    def _parse_parse_page(self, soup):
        series_season = series_episode = None

        title = soup.select_one('.movie_title')
        if title:
            title = title.text
            series_season, series_episode = self.util.extract_season_episode(title)

        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('.lang a.p1'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=self._follow_redirect(self.BASE_URL + link['href']),
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
                )

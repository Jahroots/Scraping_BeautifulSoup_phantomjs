# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import re


class Rapidtrend(SimpleScraperBase):
    BASE_URL = 'https://rapidtrend.com'
    OTHERS_URLS = ['http://rapidtrend.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        self.n += 1
        next_button_link = self._fetch_search_url(self.search_term, self.media_type, n=self.n)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _fetch_no_results_text(self):
        return u'No results found'

    def _fetch_search_url(self, search_term, media_type, n=1):
        self.n = n
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/?q={}&start={}'.format(search_term, n*10-10)

    def _parse_search_result_page(self, soup):
        for link in soup.select('.item table a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        return
        # link = soup.find('a', text='Next')
        # self.log.debug('------------------------')
        # return self._fetch_search_url(self.search_term,
        #                               self.media_type,
        #                               n=int(link['onclick'].split('navigate("n","')[1].split('"')[0])) \
        #     if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        series_season, series_episode = self.util.extract_season_episode(title)
        for link in re.findall(
            "document.write\(unescape\('(.*?)'\)\)",
            unicode(soup)
        ):
            link_soup = self.make_soup(self.util.unquote(link))
            for href in link_soup.select('a'):
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=href.href,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )

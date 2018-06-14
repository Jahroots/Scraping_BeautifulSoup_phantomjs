# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class CartelMovies(SimpleScraperBase):
    BASE_URL = 'https://cartelmovies.biz'
    OTHER_URLS = ['https://cartelmovies.net','http://cartelmovies.net', 'http://www.cartelmovies.net']
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_no_results_text(self):
        return u'0 resultados encontrados'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _fetch_search_url(self, search_term, media_type=None):
        self.search_term = search_term
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)


    def search(self, search_term, media_type, **extra):
        soup = self.make_soup(self.get(self._fetch_search_url(search_term, media_type)).text)
        self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('h3 a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def _parse_parse_page(self, soup):
        title = soup.title.text.split('|')[0].strip()
        # series_season, series_episode = self.util.extract_season_episode(title)
        for script in soup.find_all('iframe'):
            src = script['src']
            if 'http' not in src:
                src = 'http:'+src
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=src,
                                         link_text=title,
                                         # series_season=series_season,
                                         # series_episode=series_episode,
                                         )
        # like 'http://yieldmanager.adbooth.com/adserver/iframe?s=1000020871&w=468&h=60&c=1&blank=0'
        # for ifr in soup.findAll('iframe', height="60", width="468"):
                #     self.submit_parse_result(
        #         link_url=ifr['src'],
        #         link_text=title,
        #         # series_season=series_season,
        #         # series_episode=series_episode,
        #     )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PelisOnlineHD(SimpleScraperBase):
    BASE_URL = 'https://pelisonlinehd.tv'

    OTHER_URLS = [
        'http://pelisonlinehd.com',
        'http://www.pelisonlinehd.com'
        ]

    TRELLO_ID ='SMdIKfpj'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL,] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(PelisOnlineHD, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + search_term

    def X_parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link, headers={
                        'Connection': 'keep-alive'
                    }

                )
            )

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        nxt = soup.find('a', text=u'>')
        if nxt:
            return nxt['href']

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="row movies-list"] a.linker')
        if not results:
            self.submit_search_no_results()

        for link in results:
            #link = link.parent
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url, headers={
            'Connection': 'keep-alive'})
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.title').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for ifr in soup.select('div[data-player-content]'):
            aux_soup = self.make_soup(ifr['data-player-content'])
            iframes = aux_soup.select('iframe')
            for ifr in iframes:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=ifr['src'],
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

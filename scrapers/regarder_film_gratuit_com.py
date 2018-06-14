# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Regarder_film_gratuit(SimpleScraperBase):
    BASE_URL = 'http://regarder-film-gratuit.online'
    OTHER_URLS = ['http://www.regarder-film-gratuit.eu', ' http://www.regarder-film-gratuit.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self._request_connect_timeout = 600
        self._request_response_timeout = 600



    def _fetch_no_results_text(self):
        return u'Désolé, aucun article ne correspond a votre recherche'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for link in soup.select('#main .post a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post h2').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for ifr in soup.select('.content iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=ifr['src'],
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

        for link in soup.select('.content center p a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ZoneSeriesTv(SimpleScraperBase):
    BASE_URL = 'http://zoneseries.ws'
    OTHER_URLS = ['http://zoneseries.org', 'http://zoneseries.biz', 'http://zone-series.me', 'http://zone-series.tv']
    TRELLO_ID = 'dRHW1QE2'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self._request_connect_timeout = 500
        self._request_response_timeout = 500

    def _fetch_no_results_text(self):
        return u'Aucun film trouvé pour ce terme'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.serieth a'):
            soup = self.get_soup(result.href)
            links = soup.select('div.liste a')
            for link in links:
                self.submit_search_result(
                    link_url=link['href'],
                    link_title=link.text
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.pageTitle')
        season = None
        episode = None
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)

        for link in soup.select('span[id*="player_v_"] a'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['rel'][0],
                link_title=link.text,
                series_season=season,
                series_episode=episode
            )

# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TorrentSeriesOrg(SimpleScraperBase):
    BASE_URL = 'http://torrent-series.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'
        raise NotImplementedError('The account is suspended')

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'0 Resultados:'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.next.page-numbers')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.absolute-capa.no-text'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    @staticmethod
    def __find_season(text):
        srch = re.search(u'(\d+)ª Temporada', text)
        if srch:
            return srch.group(1)
        return None

    def __find_episode(self, text):
        srch = re.search(u'Episódio (\d+)', text)
        if srch:
            return srch.group(1)
        return None

    def _parse_parse_page(self, soup):
        # Grab the first image.
        for season_link in soup.select('div.entry-content a'):
            if season_link['href'].startswith(('whatsapp', 'magnet')):
                continue
            season = self.__find_season(season_link.text)
            episode = self.__find_episode(season_link.text)
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=season_link['href'],
                                     link_text=season_link.text,
                                     series_season=season,
                                     series_episode=episode,
                                     )

        for season_link in soup.select('.content.content-single p a'):
            if season_link['href'].startswith(('whatsapp', 'magnet')):
                continue
            season = self.__find_season(season_link.text)
            episode = self.__find_episode(season_link.text)
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=season_link['href'],
                                     link_text=season_link.text,
                                     series_season=season,
                                     series_episode=episode,
                                     )

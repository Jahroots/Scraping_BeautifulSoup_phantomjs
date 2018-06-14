# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SeriesPepitoTo(SimpleScraperBase):
    # Sister site to PeculasPepito.to; search is the same, but pages are a level
    # deeper.
    BASE_URL = 'https://www.seriespepito.to'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. This website merged with pelis24.mobi')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        self._parse_search_result(
            self.post(
                self.BASE_URL + '/main/searchauto',
                data={'term': search_term}
            ).json()
        )

    @staticmethod
    def _extract_season_epsisode(text):
        match = re.search('(\d+)x(\d+)', text)
        if match:
            return match.groups()
        return None, None

    def _parse_search_result(self, json_content):
        if not json_content:
            return self.submit_search_no_results()
        for result in json_content:
            series_soup = self.get_soup(result['url'])
            for episode in series_soup.select('div.accordion a.asinenlaces'):
                series_season, series_episode = \
                    self._extract_season_epsisode(episode.find('strong').text)
                self.submit_search_result(
                    link_url=episode['href'],
                    link_title=result['title'],
                    image=result['image'],
                    series_season=series_season,
                    series_episode=series_episode,
                    asset_type=ScraperBase.MEDIA_TYPE_TV
                )

    def _parse_parse_page(self, soup):
        page_title = soup.find('div', 'subtitulo').text
        series_season, series_episode = \
            self._extract_season_epsisode(page_title)
        for video_link, video_soup in self.get_soup_for_links(soup,
                                                              'table.tenlaces td.tdenlace a.enlace_link'):
            for link in video_soup.select('div.contenedor a.enlace_link'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=page_title.strip(),
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         asset_type=ScraperBase.MEDIA_TYPE_TV
                                         )

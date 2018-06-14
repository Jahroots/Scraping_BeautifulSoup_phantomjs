# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Newpct1Com(SimpleScraperBase):
    BASE_URL = 'http://newpct1.com'
    OTHERS_URLS = ['http://www.newpct1.com']
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        # Note - this does have categories, but in sub categories (ie spanish
        #  movies, us movies, etc)
        return self.BASE_URL + \
               '/buscar'

    def _fetch_no_results_text(self):
        return None#'( 0 ) Resultados encontrados'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        if link:
            return link['href']
        return None

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        soup = self.post_soup(search_url, data = {'q' : search_term})

        results = soup.select('ul.buscar-list li')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

    def __extract_season_series(self, text):
        # Temporada [ 2 ] Capitulo [ 04 ]
        srch = re.search('Temporada \[ (\d+) \] Capitulo \[ (\d+) \]', text)
        if srch:
            return srch.groups()
        return None, None

    def _parse_search_result_page(self, soup):

        for result in soup.select('ul.buscar-list li'):
            link = result.select('div.info > a')
            if not link:
                continue
            link = link[0]
            series_season, series_episode = self.__extract_season_series(
                link.text)
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text.strip(),
                image=self.util.find_image_src_or_none(result, 'a > img'),
                series_season=series_season,
                series_episode=series_episode
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        # Find a direct download link, follow and rip info out of that.
        # Note that it's not on every page...
        # Links are done like so:
        # <a href="javascript:;" onclick="popup(
        # 'http://www.newpct1.com/pct1/library/include/ajax/get_modallinks.php?links=http://ul.to/9yl753ga   http://ul.to/og9bm2lg   http://ul.to/30df0tbl   ...',950,550)" rel="nofollow" id="descargar">DESCARGAR</a>

        for link in soup.select('a#descargar'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link.href,
                link_title=link.text,
            )

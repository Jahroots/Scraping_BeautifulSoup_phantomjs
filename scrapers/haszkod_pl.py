# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Haszkod(SimpleScraperBase):
    BASE_URL = 'http://www.haszkod.pl'
    LOGIN_USER='Gotin1995'
    LOGIN_PWD = 'seek5Tae'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'pol'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        raise NotImplementedError

    def _fetch_no_results_text(self):
        return u'Nie znaleziono żadnych pozycji w bazie serwisu'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL +'/baza.php?nazwa='+ '%s' % self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' › ')
        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('table[class="lista"] a[class="lista tytul_link"]'):
            self.submit_search_result(
                link_url= self.BASE_URL + '/' + result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = self.util.get_page_title(soup)
        for link in soup.select('table.lista a[class="lista tytul_link"]'):
            season, episode = self.util.extract_season_episode(link.text)
            self.submit_parse_result(
                index_page_title = title,
                link_url = self.BASE_URL + '/' + link['href'],
                link_title = link.text,
                series_season = season,
                series_episode = episode
            )

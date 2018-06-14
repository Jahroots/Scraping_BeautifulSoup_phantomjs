# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SdilejCz(SimpleScraperBase):
    BASE_URL = 'http://sdilej.cz'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'Nebyl nalezen žádný soubor odpovídající zadaným parametrům'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Další')
        if link:
            return self.BASE_URL+link['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3 a'):
             self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        url = soup.find('a', 'page-download')['href']
        title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        self.submit_parse_result(index_page_title=title,
                                 series_season=season,
                                 series_episode=episode,
                                 link_url=self.BASE_URL+url)

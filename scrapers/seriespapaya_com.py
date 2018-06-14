# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase


class SeriespapayaCom(ScraperBase):
    BASE_URL = 'http://www.seriespapaya.com'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/busqueda/',
                data={
                    'searchquery':search_term,
                }
            )
        )

    def _parse_search_results(self, soup):
        self.block = False
        results = soup.find('div', 'cajita').find_all('div', 'capitulo-caja')
        for result in results:
            links = self.util.find_urls_in_text(result['onclick'])
            for link in links:
                ep_soup = self.get_soup(link)
                ep_links = ep_soup.select('a.visco')
                title = ep_soup.select_one('h4').text
                for ep_link in ep_links:
                    self.submit_search_result(
                        link_url=self.BASE_URL+'/'+ep_link['href'],
                        link_title=title.strip(),
                    )
                    self.block = True
        if not self.block:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            for series_links in soup.select('div.denlace a'):
                movie_soup = self.get_soup(series_links['href'])
                title = movie_soup.select_one('h1').text.strip()
                movie_links = movie_soup.find('div', text=re.compile('Ver enlace')).find_previous('div')['onclick'].split('href=')[-1].strip("'")
                season, episode = self.util.extract_season_episode(title)
                self.submit_parse_result(index_page_title=self.util.get_page_title(movie_soup),
                                         link_url=movie_links,
                                         series_season=season,
                                         series_episode=episode,
                                         )
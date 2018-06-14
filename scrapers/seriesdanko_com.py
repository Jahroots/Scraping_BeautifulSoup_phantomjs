# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SeriesdankoCom(SimpleScraperBase):
    BASE_URL = 'http://seriesdanko.to'
    OTHER_URLS = ['http://seriesdanko.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def __buildlookup(self):
        lookup = {}
        mainsoup = self.get_soup('{base_url}/all.php'.format(base_url=self.BASE_URL))
        for link in mainsoup.select('div.widget-content div[style="font-size:24px; text-align:center"] span a'):
            lookup[link.text.strip()] = self.BASE_URL + link['href']
            lookup[link.text.lower().strip()] = self.BASE_URL + link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                episodes_soup = self.get_soup(page)
                episodes = episodes_soup.find_all('div', id=re.compile('T\d+'))
                for links in episodes:
                    for link in links.select('a'):
                        self.submit_search_result(
                            link_url=link.href,
                            link_title=link.text,
                        )
                        any_results = True

        if not any_results:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return u'No he encontrado nada.'

    def _fetch_next_button(self, soup):
        return None

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h3.post-title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('table.tabla a.capitulo2'):
            redirect_soup = self.get_soup(self.BASE_URL+'/'+link.href)
            link = redirect_soup.select_one('div#url2 a')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

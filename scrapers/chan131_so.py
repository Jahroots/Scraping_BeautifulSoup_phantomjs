# coding=utf-8
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Chan131So(SimpleScraperBase):
    BASE_URL = 'http://chan131.in/'
    OTHERS_URLS = ['http://chan131.so/']
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'simpsons'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def __buildlookup(self):
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL+'watch-tv', ]):
            for serial_link in mainsoup.select('a[href*="chan131.in/watch-tv"]'):
                for ep_link in self.get_soup(serial_link.href).select('div.recent ul li a'):
                    lookup[serial_link.text.lower().strip()+' '+ep_link.text] = ep_link['href'].strip()
        return lookup

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term) or search_term in term:
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )

                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe_link in soup.select('div.iframe-container b'):
            links = self.util.find_urls_in_text(iframe_link['date-iframe'])
            for link in links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=iframe_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
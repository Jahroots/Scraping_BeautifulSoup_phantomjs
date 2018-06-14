# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DaclipsIn(SimpleScraperBase):
    BASE_URL = 'http://daclips.in'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME,  ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'Go'
    TERM = ''
    def _fetch_search_url(self, search_term, media_type):
        return None

    def _fetch_no_results_text(self):
        return u' TODO '

    def do_search(self, media_type):
        url = ''
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            url = self.BASE_URL + '/?op=videos&show=1&cat=18&block=1&time=0&per_page=50'
        elif media_type == ScraperBase.MEDIA_TYPE_FILM:
            url = self.BASE_URL + '/?op=videos&show=1&cat=1&block=1&time=0&per_page=50'
        elif media_type == ScraperBase.MEDIA_TYPE_GAME:
            url = self.BASE_URL + '/?op=videos&show=1&cat=6&block=1&time=0&per_page=50'

        soup = self.get_soup(url)
        return soup

    def search(self, search_term, media_type, **extra):
        soup = self.do_search(media_type)
        self.TERM = search_term
        self._parse_search_result_page(soup)

    def __buildlookup(self, soup):
        # Build a dict of show name -> url for the whole site.
        lookup = {}

        for link in soup.select('div.cat_item h3.t a'):
                lookup[link.text.strip()] = link['href']
                lookup[link.text.lower().strip()] = link['href']
        return lookup

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text= '»')
        if next_button:
            return self.BASE_URL + next_button.href
        return None

    def _parse_search_result_page(self, soup):
        lookup = self.__buildlookup(soup)
        search_regex = self.util.search_term_to_search_regex(self.TERM)

        any_results = False
        for term, page in lookup.items():

            if search_regex.match(self.TERM):
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True

        if not any_results:
            return self.submit_search_no_results()

        next_button = self._fetch_next_button(soup)
        self.log.debug(next_button)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        scripts = soup.select('script')
        for scp in scripts:
            if 'file:' in scp.text:
                url = scp.text.split('file:')[1].split(',')[0].replace('"', '').strip()
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )


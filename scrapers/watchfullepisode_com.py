# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WatchFullEpisode(SimpleScraperBase):
    BASE_URL = 'http://watchfullepisode.com'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise NotImplementedError('The website unreachable')
        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self._request_size_limit = (1024 * 1024 * 10) # Bytes

        raise NotImplementedError('Website Not Reachable')

    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL+ '/all-tv-shows-list/', ]):
            for link in mainsoup.select('.ddmcc ul ul li a'):
                lookup[link.text.strip()] = link['href']
                lookup[link.text.lower().strip()] = link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search ourselves
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():


            if search_regex.match(term):


                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        for item in soup.select('h3 a'):
            epis_soup = self.get_soup(item.href)

            title = epis_soup.select_one('.posttitle h1').text.strip()

            for link in epis_soup.select('.postcontent table a'):
                season, episode = self.util.extract_season_episode(title)
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

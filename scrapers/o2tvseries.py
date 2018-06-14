# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, SimpleGoogleScraperBase
from sandcrawler.scraper.caching import cacheable


class O2TVSeries(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'http://o2tvseries.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    @cacheable()
    def __build_section_lookup(self, link):
        soup = self.get_soup(link)
        lookup = {}
        for link in soup.select('div.data_list div.data a'):
            lookup[link.text] = link['href']
        next_link = soup.find('a', text='Next»')
        if next_link:
            lookup.update(
                self.__build_section_lookup(next_link['href'])
            )
        return lookup

    @cacheable()
    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            for link in mainsoup.select('div.series_set > a'):
                lookup.update(self.__build_section_lookup(link.href))
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search outselve.s
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

    @cacheable()
    def _follow_link(self, link):
        return self.get_redirect_location(link)

    def parse(self, parse_url, **extra):
        for link in self.__extract_parse_results(parse_url):
            self.submit_parse_result(
                **link
            )

    @cacheable()
    def __extract_parse_results(self, parse_url):
        soup = self.get_soup(parse_url)
        header_bar = soup.select_one('div.header_bar')
        if not header_bar or 'Seasons' not in header_bar.text:
            self.log.warning('Attempting to parse incorrect page; %s', parse_url)
            return []

        results = []

        for season_link, seasonsoup in self.get_soup_for_links(
                soup, 'div.data_list div.data a'):

            series_season = self.util.find_numeric(season_link.text)
            for episode_link, episodesoup in self.get_soup_for_links(
                    seasonsoup, 'div.data_list div.data a'):
                series_episode = self.util.find_numeric(episode_link.text)
                for link in episodesoup.select('div.data_list div.data a'):
                    # Generic ad
                    if link.text.find('UC Browser') >= 0 or link.href.find('#') >= 0:
                        continue
                    link_url = self._follow_link(link['href'])
                    if link_url:

                        # XXX TODO - hit counter
                        results.append({
                            'index_page_title': soup.title.text.strip(),
                            'link_url': link_url,
                            'link_title': link.text,
                            'series_season': series_season,
                            'series_episode': series_episode
                        }
                        )

        return results

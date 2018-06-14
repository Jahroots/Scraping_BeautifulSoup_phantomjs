# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class OneseriesTv(SimpleScraperBase):
    BASE_URL = 'http://popcornwatch.com'
    OTHER_URLS = ['http://watchseason.tv', 'http://oneseries.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def _fetch_search_url(self, search_term, media_type):
        return 

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            for link in mainsoup.select('div.show-card a'):
                lookup[link.select_one('div[class="show-card__info-name"]').text.lower().strip()] = link['href']
                #lookup[link.select_one('div.serial-list__serial-name').text.lower().strip()] = link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search ourselves
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():

            if search_regex.match(term):

                soup = self.get_soup(self.BASE_URL + page)
                videos = soup.select('div.episode-list__episodes a')
                for video in videos:
                    self.submit_search_result(
                        link_url= self.BASE_URL + video.href,
                        link_title=video.text,
                    )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(soup.select_one('h1[class="title"]').text)
        for link in soup.select('source'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                season = season,
                episode = episode
            )

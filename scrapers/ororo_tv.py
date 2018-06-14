from sandcrawler.scraper import ScraperBase

class OrOroTv(ScraperBase):

    BASE_URL = 'https://ororo.tv'
    OTHER_URLS = ['https://ororo.tv/en/movies']
    SINGLE_RESULTS_PAGE = True
    REFERER = None

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)


    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            for link in mainsoup.select('div[class="shows"] a'):
                lookup[link.text.strip()] = self.BASE_URL + link['href']
                lookup[link.text.lower().strip()] = self.BASE_URL + link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        self.REFERER = None

        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                soup = self.make_soup(self.get(page).text)
                episodes = soup.select('div.episode-box a[data-id]')
                for episode in episodes:
                    self.submit_search_result(
                        link_url = self.BASE_URL + episode['data-href'],
                        link_title = episode.text
                    )
                any_results = True

        if not any_results:
            self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        self.REFERER = parse_url.split('videos')[0] #header to be able to catch the video src
        soup = self.get_soup(parse_url)
        episodes = soup.select('video')
        for episode in episodes:
            self.submit_parse_result(
                                 link_url = episode.select_one('source')['src'],
                                 link_title = episode['data-title']
                                 )
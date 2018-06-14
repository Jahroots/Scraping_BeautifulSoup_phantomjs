from sandcrawler.scraper import ScraperBase

class SerienStream(ScraperBase):
    BASE_URL = 'https://serienstream.to'

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):

        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():

            if search_regex.match(term):
                self.log.debug(page)
                soup = self.get_soup(page)
                sources = soup.select('td.seasonEpisodeTitle a[href*="/serie/"]')

                if not sources or len(sources) == 0:
                    return self.submit_search_no_results()

                for source in sources:
                    self.submit_search_result(
                        link_url=self.BASE_URL + source['href'],
                        link_title=source.text.strip()
                    )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        videos = soup.select('li[data-link-id] a')
        for video in videos:
            url = self.get_redirect_location(self.BASE_URL + video['href'])
            self.submit_parse_result(
                index_page_title = soup.title.text.strip(),
                link_url = url,
                link_title=video.select_one('h4').text
            )

    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        search_url = 'http://serienstream.to/serien'
        for mainsoup in self.soup_each([search_url, ]):
            for link in mainsoup.select('div.genre a'):
                lookup[link.text.strip()] = self.BASE_URL + link['href']
                lookup[link.text.lower().strip()] = self.BASE_URL + link['href']
        return lookup
from sandcrawler.scraper import ScraperBase

class WatchMovieFull(ScraperBase):

    BASE_URL = 'http://www.movieshdwatch.net'
    OTHERS_URL = ['http://www.movieswatchonline.org', 'http://www.hdfreemovies.org', 'http://www.watchmoviefull.com']


    #No Pagination found
    SINGLE_RESULTS_PAGE = True
    ALLOW_FETCH_EXCEPTIONS = True


    #Standard set up
    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.proxy_region = 'eng'

    # Search base method
    def search(self, search_term, media_type, **extra):
        # submit the search
        search_url = self.BASE_URL + '/page/REPLACE/?s=' + search_term
        replace = 1

        # pagination
        while self.connect_to(search_url.replace('REPLACE', str(replace))):
            movies = self.soup.select('div.item a[href]')
            posters = self.soup.select('div.item img[src]')

            if not movies:
                self.submit_search_no_results()
                return

            for index, movie in enumerate (movies):
                image = None
                if posters and len(posters) > index:
                    image = posters[index]['src']

                self.submit_search_result(
                    link_url = movie['href'],
                    link_title = movie.text.strip(),
                    image = image
                )
            replace += 1


    def parse(self, page_url, **extra):
        self.soup = self.get_soup(page_url)
        video = self.soup.select_one('iframe')

        if video:
            self.submit_parse_result(index_page_title = self.soup.title.text.strip(),
                                     link_url = video['src']
                                     )
        return None


    def connect_to(self, search_url):
        try:
            self.soup = self.get_soup(search_url)
            if self.soup.select_one('div.no_contenido_home'):
                self.submit_search_no_results()
                return False
        except Exception:
            return False
        return True

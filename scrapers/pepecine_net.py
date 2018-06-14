from sandcrawler.scraper import ScraperBase


class PepeCine(ScraperBase):
    BASE_URL = 'https://pepecine.io'
    OTHERS_URLS = [
        'https://pepecine.online',
        'http://pepecine.net'
    ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in self.OTHERS_URLS + [self.BASE_URL, ]:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)


    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/donde-ver?q=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        movies = soup.select('div.tab-pane figcaption a')

        if not movies or len(movies)== 0:
            return self.submit_search_no_results()

        for result in movies:
            if 'ver-serie-tv' in result['href']:
                show_soup = self.get_soup(result['href'])
                for season in show_soup.select('div.heading a.sezon'):
                    season_soup = self.get_soup(season.href)
                    for episode in season_soup.select('ul#episode-list h4.media-heading a'):
                        self.submit_search_result(
                            link_url=episode.href,
                            link_title=episode.text,
                        )
            else:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text,
                )


    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        #we must get the movie url from a javascript function
        for result in soup.select('a[data-bind*="click"]'):
            raw_string = result['data-bind']

            if "http" in raw_string:
                start = raw_string.index('http')
                raw_string = raw_string[start : len(raw_string)]
                end = raw_string.index("',")
                raw_string = raw_string[:end]
            else:
                continue
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url = raw_string,
                                     link_title = result.text
                                     )
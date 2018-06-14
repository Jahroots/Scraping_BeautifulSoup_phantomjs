#coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase

class WatchmovieIs(SimpleScraperBase, ScraperBase):

    BASE_URL = 'http://watchmovie.today'
    OTHER_URLS = ['http://watchmovie.ms', 'http://watchmovie.is']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website no longer available')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)
            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)


    def search(self, search_term, media_type, **extra):
        data = {'q': '{}'.format(search_term)}
        search_url = self.BASE_URL + '/search_movies'
        self._parse_search_results(self.post_soup(search_url, data=data))


    def _parse_search_results(self, soup):
        if soup.find(text = u'here >>>') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('div.afishome a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result['title']
            )

        next_link = soup.find('a', text=u'>')
        if next_link and self.can_fetch_next():
            self._parse_search_results(self.get_soup(
                self.BASE_URL + next_link['href']
            ))


    def _parse_parse_page(self, soup):
       for link in soup.select('strong.movie_version_link a'):
           if '.php' in link.href:
               continue
           movie_soup = self.get_soup(link.href)
           movie_link = movie_soup.find('frame', id='play_bottom')['src']
           self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=movie_link)

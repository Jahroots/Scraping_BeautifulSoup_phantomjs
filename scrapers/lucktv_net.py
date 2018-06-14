# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class LucktvNet(SimpleScraperBase):
    BASE_URL = 'http://lucktv.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_NAME = 'Otile1954'
    PASSWORD = 'AiBee6rai'
    EMAIL = 'roxannedmorton@jourrapide.com'

    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL + '/searchlist.php',
            data={
                'q':search_term})

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _login(self):
        soup = self.get_soup(self.BASE_URL + '/login.php')
        token = soup.select_one('input[id*="TokenFields"]')['value']

        soup = self.post_soup(self.BASE_URL + '/reg.php', data={'_method': 'POST',
                                                                'Token1935871008': 'login',
                                                                'UserUsername': self.USER_NAME,
                                                                'subscriptionsPass': self.PASSWORD,
                                                                'data[_Token][fields]': token
                                                                })

    def search(self, search_term, media_type, **extra):
        #Log in
         soup = self.get_soup(self.BASE_URL + '/login.php')
         token = soup.select_one('input[id*="TokenFields"]')['value']

         soup = self.post_soup(self.BASE_URL + '/reg.php', data = {'_method' : 'POST',
                                                                   'Token1935871008' : 'login',
                                                                   'UserUsername' : self.USER_NAME,
                                                                   'subscriptionsPass': self.PASSWORD,
                                                                   'data[_Token][fields]' : token
                                                                   })
         self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.index_main-right-lb ul li'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.detailed_main-left-Season-list ul li a'):
            self._login()
            script_text=None
            try:
                script_text = self.get_soup(self.BASE_URL+result.href).select_one('div#ipadvideo').find_next('script').text
            except AttributeError:
                pass
            if script_text:
                movie_links = self.util.find_urls_in_text(script_text)
                for movie_link in movie_links:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=movie_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

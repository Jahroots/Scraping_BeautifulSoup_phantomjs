# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class ZalukajCom(SimpleScraperBase):
    BASE_URL = 'https://zalukaj.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    USERNAME = 'Hessity'
    PASSWORD = 'joh7Ac2uwie'

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL)
        if 'Wyloguj' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            self.post(self.BASE_URL + '/account.php',
                                     data={
                                            'login': username,
                                            'password': PASSWORD,
                                            }
                                     )

    def _fetch_no_results_text(self):
        return u'Niestety w naszej bazie nie ma podanego filmu'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.post_soup(
            self.BASE_URL + '/szukaj',
            data={
                'searchinput':self.util.quote(search_term),
            }
        )
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
       for result in soup.select('div.tivief4 a'):
           if 'https' not in result.href:
               url = 'https:'+result.href
               self.submit_search_result(
                    link_url=url,
                    link_title=result.text,
                )

    def _parse_parse_page(self, soup):
        self._login()
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div#pw_title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        iframe_link = self.BASE_URL+soup.select_one('iframe')['src']+'&x=1'
        iframe_link_soup = self.get_soup(iframe_link)
        for link in iframe_link_soup.select('div#free_player iframe'):
            url = link['src']
            if 'http' not in url:
                url = 'http:'+url
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

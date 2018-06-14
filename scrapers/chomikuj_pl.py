# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ChomikujPl(SimpleScraperBase):
    BASE_URL = 'http://chomikuj.pl'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USERNAME = 'Theltorither58'
    PASSWORD = 'ei4ahDi6'
    USER_AGENT_MOBILE = False

    def setup(self):
        super(self.__class__, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 400

    def get(self, url, **kwargs):
        return super(ChomikujPl, self).get(url, allowed_errors_codes=[404,], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No results found'


    def _login(self):
        home_soup = self.get_soup(self.BASE_URL)
        for i in range(0, 5):
            if not home_soup.select_one('input[name="__RequestVerificationToken"]'):
                home_soup = self.get_soup(self.BASE_URL)
            else:
                break

        token = home_soup.select_one('input[name="__RequestVerificationToken"]')['value']
        if u'Wiadomości' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            self.post(self.BASE_URL + '/action/Login/TopBarLogin',
                                     data={
                                            '__RequestVerificationToken': token,
                                            'ReturnUrl': '/Theltorither58',
                                            'Login': username,
                                            'Password': PASSWORD,
                                            }
                                     )

        return token

    def _do_search(self, search_term, token, page=0):
        return self.post_soup(
            self.BASE_URL + '/action/SearchFiles',
            data={'IsGallery': False, 'FileType':'video', 'FileName':self.util.quote(search_term),
                  'Page': '{}'.format(page), '__RequestVerificationToken':token}
        )

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        token = self._login()
        first_page = self._do_search(search_term, token)
        if unicode(first_page).find(u'Nie znaleziono pliku') >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(first_page)
        page = 1
        while self.can_fetch_next():
            page += 1
            soup = self._do_search(
                search_term,
                page
            )
            if not self._parse_search_result_page(soup):
                return


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.filerow h3'):
            link = result.select_one('a')
            if 'ebookpoint.pl' not in link.href:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link = soup.select_one('video.fid-info')
        if link:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['rel'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        link = soup.select_one('a[title="Download"]')
        if link:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
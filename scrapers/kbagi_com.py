# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json
class KbagiCom(SimpleScraperBase):
    BASE_URL = 'http://kbagi.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'TODO'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LOGIN_URL = '/action/Account/Login?returnUrl=%2F'
    LOCATION_FILE = '/action/DownloadFile?location=fi&f=%s'
    USER_NAME = 'Mathe1950'
    PASSWORD = 'aiChu3ojoo'
    EMAIL = 'RobertoJCrump@dayrep.com'
    PAGE = 1
    OFF = False

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/action/SearchFiles'

    def _fetch_no_results_text(self):
        return u'Unable to results'

    def _fetch_next_button(self, soup):
        return None

    def next_soup(self):
        self.PAGE += 1
        soup = self.post_soup(self._fetch_search_url(self.search_term, self.media_type), data={'Mode': 'Gallery',
                                                                                     'Phrase': self.search_term,
                                                                                     'ref': 'pager',
                                                                             'pageNumber' : self.PAGE   })
        return soup

    def search(self, search_term, media_type, **extra):
        self.OFF = False
        self.PAGE = 1
        self.search_term = search_term
        self.media_type = media_type

        #Login
        soup = self.get_soup(self.BASE_URL)
        token = soup.select_one('input[name="__RequestVerificationToken"]')['value']

        soup = self.post_soup(self.BASE_URL + self.LOGIN_URL, data = {
            '__RequestVerificationToken': token,
            'UserName': self.USER_NAME,
            'Password': self.PASSWORD
        })

        self.log.debug(soup.select_one('div.user_info').text)

        #search
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {'Mode' : 'Gallery',
                                                                                       'Phrase': search_term,
                                                                                       'ref' : 'pager'})
        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('#SearchGallery h2.name')

        if not results or len(results) == 0:
            self.OFF = True
            self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            self.submit_search_result(
                link_url= self.BASE_URL + link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        # Pagination
        if not self.OFF:
            soup = self.next_soup()
            self.log.debug('--------------------------------')
            if soup and self.can_fetch_next():
                self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.file_content h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
        fileId = soup.select_one('input[name="fileId"]')['value']
        soup = self.get_soup(self.BASE_URL)
        b_token = soup.select_one('input[name="__RequestVerificationToken"]')['value']

        soup = self.post_soup(self.BASE_URL + self.LOGIN_URL, data={
            '__RequestVerificationToken': b_token,
            'UserName': self.USER_NAME,
            'Password': self.PASSWORD
        })

        self.log.debug(soup.select_one('div.user_info').text)

        text = self.post(self.BASE_URL + self.LOCATION_FILE %fileId, data = {'fileId' : fileId,
                                                                                  '__RequestVerificationToken': token}).text
        link_url = None
        try:
            link_url = json.loads(text)['DownloadUrl']
        except ValueError:
            pass
        if link_url:
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= json.loads(text)['DownloadUrl'],
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
            )

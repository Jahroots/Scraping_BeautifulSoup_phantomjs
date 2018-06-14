# coding=utf-8
import base64
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase, CachedCookieSessionsMixin
import re

class LiensSeriesCom(CachedCookieSessionsMixin, OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.liens-series.com'
    OTHER_URLS = ['https://liens-series.com','http://www.liens-series.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False
    USER_NAME = 'Contich85'
    PASSWORD = 'aiVuoNgiw6ai'
    EMAIL = 'kathleenmjennings@armyspy.com'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u"La recherche n'a retourn"

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _login(self):
        soup = self.post_soup(self.BASE_URL, data = {'login_name' : self.USER_NAME, 'login_password' : self.PASSWORD, 'login' : 'submit'})
        self.save_session_cookies()

    def search(self, search_term, media_type, **extra):
        self._login()
        self.load_session_cookies()
        super(LiensSeriesCom, self).search(search_term, media_type, **extra)


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.main-news'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def parse(self, parse_url, **extra):
        self._login()
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        links = soup.select('a[href*="engine/go.php?url="]')
        for link in links:
            try:
                base_url = self.get_redirect_location(link.href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=base_url,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
                self.log.debug(base_url)
            except Exception as e:
                self.log.debug(str(e))





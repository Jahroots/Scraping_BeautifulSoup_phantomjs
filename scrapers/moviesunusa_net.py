# coding=utf-8

from sandcrawler.scraper import ScraperBase, DuckDuckGo, SimpleGoogleScraperBase, CloudFlareDDOSProtectionMixin, SimpleScraperBase
import re

class MoviesunusaNet(DuckDuckGo):
    BASE_URL = 'http://moviesunus01.com'
    OTHER_URLS = ['http://moviesunuss.net']

    OTHER_URLS = ['http://moviesunus.net', 'http://moviesunkd.net', 'http://www.moviesunkd.net','http://moviesunusa.net', 'http://www.moviesunusa.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'zho'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_NAME = 'mm18'
    PASSWORD = 'sun'
    LOG_URL = ''

    def setup(self):
        super(MoviesunusaNet,self ).setup()
        self._request_connect_timeout = 600
        self._request_response_timeout = 600

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 521], **kwargs)

    def _login(self, redirect_to):
        data = {'log': 'mm18', 'pwd': 'sun', 'wp-submit': 'Login+%C2%BB', 'redirect_to': self.BASE_URL + redirect_to}
        soup = self.post_soup(self.BASE_URL + '/wp-login.php', data=data)
        return soup

    def _parse_parse_page(self, soup):
        redirect_to = soup.select_one('input[name="redirect_to"]')
        if redirect_to:
            redirect_to=redirect_to['value']
            if u'需先登入,才能收看' in unicode(soup):
                soup = self._login(redirect_to)

            index_page_title = self.util.get_page_title(soup)
            series_season, series_episode = self.util.extract_season_episode(index_page_title)
            for iframe in soup.select('iframe'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src'],
                    series_season=series_season,
                    series_episode=series_episode,
                )
            for script in soup.select('script'):
                if 'iframe' in script.text:
                    for src in re.findall('src="(.*?)"', script.text):
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=src,
                            series_season=series_season,
                            series_episode=series_episode,
                        )

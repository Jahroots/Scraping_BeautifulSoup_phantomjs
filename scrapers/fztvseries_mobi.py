# coding=utf-8

from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase, VBulletinMixin, CloudFlareDDOSProtectionMixin, SimpleGoogleScraperBase
import requests

class FztvseriesMobi( SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'https://www.fztvseries.mobi'
    OTHER_URLS = ['https://fztvseries.mobi']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    REQUIRES_WEBDRIVER = ('parse',)
    WEBDRIVER_TYPE = 'phantomjs'


    def parse(self, parse_url, **extra):
        self.webdriver().get(parse_url.replace('https:', 'http:'))

        soup = self.make_soup(self.webdriver().page_source)
        if 'subfolder.php' in parse_url:
            files = soup.select('a[href*="files"]')
            for file in files:
                self.webdriver().get(self.BASE_URL + '/' + file.href)
                soup = self.make_soup(self.webdriver().page_source)
                self._parse_parse_page(soup)
        else:
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('textcolor1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        episodes = soup.select('ul.filesboxul a[href*="episode.php"]')
        for episode in episodes:
            self.webdriver().get(self.BASE_URL.replace('https:', 'http:') + '/' +  episode.href)
            soup = self.make_soup(self.webdriver().page_source)
            links = soup.select('a[href*="download"]')
            for link in links:
                self.webdriver().get(self.BASE_URL.replace('https:', 'http:') + '/' + link.href)
                soup = self.make_soup(self.webdriver().page_source)
                for file in soup.select('a[href*="down"]'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=file.href,
                        link_title=file.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
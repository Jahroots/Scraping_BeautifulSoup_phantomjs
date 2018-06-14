# -*- coding: utf-8 -*-
import time
from sandcrawler.scraper import ScraperAuthException
from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin, CachedCookieSessionsMixin


class WareznetCz(SimpleScraperBase, VBulletinMixin, CachedCookieSessionsMixin):
    BASE_URL = 'http://wareznet.cz'
    USERNAME = 'Factiven'
    PASSWORD = 'woe0Iesool'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'slo'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _login(self):
        soup = self.get_soup('http://wareznet.cz/ucp.php?mode=login')
        if u'Odhlásit se' not in unicode(soup):
            sid = soup.find('input', attrs={'name': "sid"})['value']
            self.post(
                self.BASE_URL + '/ucp.php?mode=login',
                data={'username': self.USERNAME,
                      'password': self.PASSWORD,
                      'login': 'Login',
                      'redirect': 'index.php',
                      'sid':sid
                      }
            )

    def search(self, search_term, media_type, **extra):
        self._login()
        return super(WareznetCz, self).search(search_term, media_type, **extra)

    def _fetch_no_results_text(self):
        return u'Nalezeno 0 výsledků hledání'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?keywords=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[rel="next"]')
        if link:
            return self.BASE_URL + link['href'][1:]
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.postbody h3 a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'][1:],
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for post in soup.select('div.codebox code'):
            for link in self.util.find_urls_in_text(post.text):
                for movie_link in link.split('http')[1:]:
                    if '/prehled/' in movie_link:
                        continue
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_url='http'+movie_link,
                                             link_title='http'+movie_link,
                                             series_season=series_season,
                                             series_episode=series_episode
                                             )

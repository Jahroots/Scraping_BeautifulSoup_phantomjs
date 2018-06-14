# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FightvideoMmatdCom(SimpleScraperBase):
    BASE_URL = 'http://fight.mmashare.club'
    OTHER_URLS = ['http://fightvideo.mmatd.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = 'cesar'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]
    USERNAME = 'Woulgethater1948'
    PASSWORD = 'Ohfoduatei3'

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search.php?keywords={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No suitable matches were found'

    def _login(self):
        soup = self.get_soup(self.BASE_URL)
        if u'Logout' not in unicode(soup):
            self.post(
                'http://fight.mmashare.club/ucp.php?mode=login',
                data={'username': self.USERNAME,
                      'password': self.PASSWORD,
                      'login': 'Login',
                      'redirect': './ucp.php?mode=register',
                      }
            )

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[rel="next"]')
        if next_button:
            return self.BASE_URL+next_button.href[1:]
        return None

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        self._login()
        soup = self.get_soup('{base_url}/search.php?keywords={search_term}'.format(base_url=self.BASE_URL,
                                                                            search_term=self.util.quote(search_term)))
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        found=0
        if 'Please try again in' in str(soup):
            self.log.warn('waiting...')
            time.sleep(int(str(soup).split('again in ')[1].split(' seconds')[0]) + .5)
            soup = self.get_soup(soup._url)
        for result in soup.select('div.postbody'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=self.BASE_URL+link.href[1:],
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        self._login()
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('a.postlink'):
            if 'http' in result.text:
                link = result.href
                if 'wikipedia' in result.text:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for result in soup.select('div.postbody div.content'):
            links = self.util.find_urls_in_text(result.text)
            for link in links:
                if '.jpg' in link or '.png' in link or self.BASE_URL in link or 'mmavideofights' in link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

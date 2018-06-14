# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import CachedCookieSessionsMixin, CacheableParseResultsMixin
from sandcrawler.scraper.caching import cacheable
import base64


class TopserialySk(CacheableParseResultsMixin, SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'https://www.topserialy.to'
    OTHER_URLS = ['https://www.topserialy.sk', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'slo'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USERNAME = 'Antra1950'


    def _login(self):
        token_soup = self.get_soup('{}/login'.format(self.BASE_URL))
        name = ''
        try:
            name = token_soup.find('span', 'head-name ')
        except AttributeError:
            pass
        if not name:
            token = token_soup.find('form', attrs={'method':'post'}).find('input', attrs={'name':'token'})['value']
            soup = self.post_soup(self.BASE_URL + '/login',
                      data=dict(user_name='Antra1950',user_pass='vieJeiph0',remember='1',action='login',token=token,
                      redirect='',submit='' ))

        self.save_session_cookies()

    def _check_login(self):
        self.load_session_cookies()
        response = self.get(self.BASE_URL)
        if self.USERNAME not in response.content:
            self._login()


    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?search={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self._check_login()
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _parse_search_results(self, soup):
        blocks = soup.select('a')
        if not blocks:
            return self.submit_search_no_results()
        for block in blocks:
            link = self.BASE_URL+block['href']
            soup = self.get_soup(link)
            episodes_list = []
            try:
                episodes_list = soup.find_all('div', 'accordion')
            except AttributeError:
                pass
            if episodes_list:
                for episode_list in episodes_list:
                    episode_link = episode_list.find('p')['data']
                    episode_soup = self.get_soup(self.BASE_URL + episode_link)
                    episodes_table = []
                    try:
                        episodes_table = episode_soup.find_all('a')
                    except AttributeError:
                        pass
                    if episodes_table:
                        for episode_table in episodes_table:
                            movie_link = '{}/{}'.format(self.BASE_URL, episode_table['href'])
                            season, episode = self.util.extract_season_episode(movie_link)

                            self.submit_search_result(
                                    link_url=movie_link,
                                    link_title=self.util.get_page_title(soup),
                                    series_season=season,
                                    series_episode=episode
                                )

    @cacheable()
    def _follow_link(self, url, parse_url):
        return self.get_redirect_location(
            url,
            headers={'referer': parse_url}
        )

    def parse(self, parse_url, **extra):
        self._check_login()
        return super(TopserialySk, self).parse(parse_url, **extra)

    def _parse_parse_page(self, soup):
        for iframe in soup.select('iframe[data-src]'):
            base = iframe['data-src']
            base = base64.decodestring(base)
            url = self._follow_link(base, soup._url)
            if url:
                title = soup.find('h1', 'h1epizoda').text.strip()
                index_page_title = self.util.get_page_title(soup)
                season, episode = self.util.extract_season_episode(title)

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                    link_url=url
                )


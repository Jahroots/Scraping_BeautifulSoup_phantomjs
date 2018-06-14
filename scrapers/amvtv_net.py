# coding=utf-8
import re
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class AmvtvNet(SimpleScraperBase):
    BASE_URL = 'http://amvtv.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'rus'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('The website is out of reach')

    def _do_search(self, search_term):
        time.sleep(3)
        return self.post_soup(
            self.BASE_URL + '/search.php',
            data={
                'nm':'{}'.format(search_term), 'allw':'1', 'pn':'', 'f[]': '0', 'tm':'0', 'dm': '0', 'o':'1', 's':'0',
                'submit':u'Ïîèñê'})

    def _fetch_no_results_text(self):
        return u'Подходящих тем или сообщений не найдено'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('a.topictitle'):
            self.submit_search_result(
                link_url=self.BASE_URL+result.href[1:],
                link_title=result.text,
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
        for magnet_link in soup.find_all('b', text=re.compile('MAGNET')):
            link = magnet_link.find_previous('a')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json

class AndroidVshareCom(SimpleScraperBase):
    BASE_URL = 'http://www.vsgamemarket.com'
    OTHER_URLS = ['http://android.vshare.com']
    SCRAPER_TYPES = [SimpleScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    PAGE = 1
    SEARCH_TERM = ''


    def _fetch_search_url(self, search_term, media_type):
        return None
    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def do_search (self):
        text = self.post(self.BASE_URL + '/ajax_get_search/', data={'keyword': self.SEARCH_TERM,
                                                             'page': self.PAGE}).text
        return json.loads(text)

    def search(self, search_term, media_type, **extra):
        self.PAGE = 1
        self.SEARCH_TERM = search_term

        data = self.do_search()


        if not 'data_list' in data:
            return self.submit_search_no_results()

        self._parse_search_result_page(data)

    def _parse_search_result_page(self, data):

        for item in data['data_list']:

            if 'screenkey' in item:
                self.submit_search_result(
                    link_url=self.util.canonicalise(self.BASE_URL, item['name_url']),
                    link_title=item['name'],
                    image=item['screenkey'][0]['picture'],
                )
            else:
                self.submit_search_result(
                    link_url=self.util.canonicalise(self.BASE_URL, item['name_url']),
                    link_title=item['name'],
                )

        self.PAGE += 1
        data = self.do_search()
        if data and len(data['data_list']) > 0 and self.can_fetch_next():
            self._parse_search_result_page(data)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.xiazce a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

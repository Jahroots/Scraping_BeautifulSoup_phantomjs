# coding=utf-8
import re
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import time

class HayhaytvVn(SimpleScraperBase):
    BASE_URL = 'http://www.hayhaytv.vn'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(HayhaytvVn, self).setup()
        self._request_connect_timeout = 500
        self._request_response_timeout = 500

    def get(self, url, **kwargs):
        return super(HayhaytvVn, self).get(url, allowed_errors_codes=[403, 502, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/tim-kiem.html?term={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.block-base'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
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
        film_key_text = soup.select_one('div#play_video')

        if film_key_text and film_key_text.find_next('script') and film_key_text.find_next('script').text:
            film_key_text = film_key_text.find_next('script').text
            film_key = film_key_text.split('var FILM_KEY =')
            if film_key and len(film_key) > 0:
                film_key = film_key[1].split(";")[0].replace("'", '').strip()
                headers = {'Referer':soup._url}
                source_urls = json.loads(self.get_soup('http://www.hayhaytv.vn/getsource/{}?ip=190.73.5.16'.format(film_key), headers=headers).text)['sources']
                self.log.debug(source_urls)
                for source_url in source_urls:
                        movie_link = source_url['file']
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=movie_link,
                            link_title=movie_link,
                            series_season=series_season,
                            series_episode=series_episode,
                        )

class HdsieunhanhCom(HayhaytvVn, SimpleScraperBase):
    BASE_URL = 'http://www.hdsieunhanh.com/'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        film_key_text = soup.select_one('div#play_video')
        if film_key_text:
            film_key_text = film_key_text.find_next('script').text
            film_key = re.search("""var FILM_KEY = \'(.*)_';\s?[var source]?""", film_key_text).groups(0)[0]
            headers = {'Referer':soup._url}

            text = self.get(
                'http://www.hdsieunhanh.com/getsource/{}__?ip=186.90.134.75&preloadPlayer=1&fix=1'.format(film_key),
                headers=headers).text
            
            if 'sources' in text:
                source_urls = json.loads(text)['sources']

                for source_url in source_urls:
                    movie_link = source_url['file']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=movie_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

            time.sleep(5)


# coding=utf-8
import urlparse
import re
import hashlib, time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DayazMedia(SimpleScraperBase):
    BASE_URL = 'https://dayaz.media'
    OTHER_URLS = ['http://dayaz.media', 'http://us.dayaz.media', 'http://dayaz.media', 'https://dayaz.media']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
    LONG_SEARCH_RESULT_KEYWORD = 'man'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one(' TODO ')
        if next_button:
            return next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/search', data = {'q': search_term, '92b6a9ec1bdc028388c72f3ce3e586e4' : 'be8c2db2d45565fff3459fcc45d24b3c>', '92b6a9ec1bdc028388c72f3ce3e586e4_hash': '4c7c0fcd67ff2492732447ac1b0775199b664a6b'}, headers= {'User-Agent': self.USER_AGENT})

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.carouselItemV2'):
            link = result.select_one('a')
            if '/serial/' in link.href:
                season_urls = soup.select('a.watchOnlineBtn')
                for season_url in season_urls:
                    series_soup = self.get_soup(season_url.href)
                    for series_link in series_soup.select('a.singleSerialItem'):
                        self.submit_search_result(
                            link_url=series_link.href,
                            link_title=series_link.text,
                            image= self.BASE_URL + self.util.find_image_src_or_none(result, 'img'),
                        )
            else:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        path = urlparse.urlparse(soup._url).path
        scripts_text = soup.select('div#all_videos_wrapper script')
        for script_text in scripts_text:
            movie_links = re.findall("""src="(.*)='""", script_text.text)
            for movie_link in movie_links:
                movie_link = 'http:'+movie_link+'='+path
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=movie_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

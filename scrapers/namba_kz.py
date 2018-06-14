# coding=utf-8
import json
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class NambaKz(SimpleScraperBase):
    BASE_URL = 'http://namba.kz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_AGENT_MOBILE = False


    def _fetch_no_results_text(self):
        return u'[]'

    def _fetch_search_url(self, search_term, media_type=None, start=0):
        self.start = start
        self.search_term = search_term
        for media_type in self.MEDIA_TYPES:
            if 'tv' in media_type:
                return self.BASE_URL+'/api/?query={}&type=video&service=home&action=search&token=aYJa8nosL0l9nLc7&limit=15&offset={}&sort=desc'.format(self.util.quote(search_term), start)
            else:
                return self.BASE_URL+'/api/?query={}&type=movie&service=home&action=search&token=aYJa8nosL0l9nLc7&limit=15&offset={}&sort=desc'.format(self.util.quote(search_term), start)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 15
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        if 'video' in soup._url:
            results = json.loads(soup.text)
            for result in results:
                id_link = result['id']
                link_title = result['title']
                link = 'http://namba.kz/video_player.php?id={}&nambaPlayer=0'.format(id_link)
                self.submit_search_result(
                        link_url=link,
                        link_title=link_title,
                        image=result['image'].replace('\\', ''),
                    )
        if 'movie' in soup._url:
            results = json.loads(soup.text)
            for result in results:
                id_link = result['id']
                link_title = result['title']
                link = 'http://namba.kz/movie/watch.php?id={}'.format(id_link)
                self.submit_search_result(
                    link_url=link,
                    link_title=link_title,
                    image=result['preview'].replace('\\', ''),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        param_url = re.search("""value="config=(.*)\"""", unicode(soup)).groups()[0]
        movie_link = json.loads(self.get_soup(param_url).text)['playlist'][1]['url']
        self.submit_parse_result(
            index_page_title=index_page_title,
            link_url=movie_link,
            link_title=title.text,
            series_season=series_season,
            series_episode=series_episode,
        )

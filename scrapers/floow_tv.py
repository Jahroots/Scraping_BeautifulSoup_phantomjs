# -*- coding: utf-8 -*-
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Floow_TV(SimpleScraperBase):
    BASE_URL = 'http://floow.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    DATA_KEYS = {"key":"73894672jdjhjdddddfhd"}
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError("the website is deprecated. They did windows application")


    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type=None):
            if 'film' in media_type:
                self.search_term = search_term
                return self.BASE_URL + '/apimovies/moviebyword/{}/200'.format(search_term)
            if 'tv' in media_type:
                self.search_term = search_term
                return self.BASE_URL + '/apiseries/seriebyword/{}/200'.format(search_term)

    def _do_search(self, search_term):
        for m_type in self.MEDIA_TYPES:
            token = json.loads(self.post_soup('http://floow.tv/apibase/token', data=self.DATA_KEYS).text)['token']
            links = self._fetch_search_url(search_term, media_type=m_type)
            self.DATA_KEYS['token'] = token
            return self.post(links, data=self.DATA_KEYS)


    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        results = json.loads(soup.text)['results']
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['link'],
                link_title=result['title'],
                image=result['poster']
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        if '/serie/' in soup._url:
            nav_ids = soup.select('div.mini_nav_bt')
            for nav_id in nav_ids:
                navigation_id = None
                try:
                    navigation_id = nav_id['data-id']
                except KeyError:
                    pass
                if navigation_id:
                    temp_chaps_soup = json.loads(self.post_soup('http://floow.tv/apiseries/tempchapters/{}'.format(navigation_id), data=self.DATA_KEYS).text)
                    results = temp_chaps_soup['results']
                    for result in results:
                        urls = self.get_soup(self.BASE_URL+'/stream/selector/{}/2'.format(result['id'])).select('div.sel_container a.option')
                        for url in urls:
                            link = url['href']
                            if 'http' not in link:
                                link = self.BASE_URL+link
                            movie_link_soup = self.get_soup(link)
                            file_link = None
                            try:
                                file_link = movie_link_soup.find_all('iframe')[-1]['src']
                            except IndexError:
                                pass
                            if not file_link:
                                file_link = movie_link_soup.text.split("'file' : ")[-1].split('",')[0].strip('"')
                            series_episode = result['number']
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=file_link,
                                link_title=file_link,
                                series_season=series_season,
                                series_episode=series_episode,
                            )
        if '/pelicula/' in soup._url:
            iframe_source = soup.select_one('iframe#stream')['src'].split('/')[-1]
            urls = self.get_soup(self.BASE_URL+'/stream/selector/{}'.format(iframe_source)).select('div.sel_container a.option')
            for url in urls:
                link = url['href']
                if 'http' not in link:
                    link = self.BASE_URL+link
                movie_link_soup = self.get_soup(link)
                try:
                    file_link = movie_link_soup.find_all('iframe')[-1]['src']
                except IndexError:
                    file_link = movie_link_soup.text.split("'file' : ")[-1].split('",')[0].strip('"')
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=file_link,
                    link_title=file_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )



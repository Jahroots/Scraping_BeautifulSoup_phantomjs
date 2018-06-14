#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase


class EkinoTVBase(ScraperBase):

    BASE_URL = 'http://ekino.tv'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        raise NotImplementedError('Redirects to http://seans.pl')


        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _season_episode_from_url(self, url):
        m = re.search('.*sezon,(\d+),epizod,(\d+).*', url)
        if m:
            return m.groups()
        return (None, None)

    def _parse_parse_page(self, soup):
        for video_link in soup.select('ul.players > li > a'):
            video_soup = self.get_soup(self.BASE_URL + '/' + video_link['href'])
            # Could probably skip this for film...
            season_num, episode_num = self._season_episode_from_url(
                video_link['href']
            )
            for iframe in video_soup.select('div#free_player iframe'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_title=self.util.get_page_title(soup),
                                         link_url=iframe['src'],
                                         series_season=season_num,
                                         series_episode=episode_num,
                                         )



class EkinoTVTV(EkinoTVBase):

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        super(EkinoTVTV, self).setup()

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/szukaj-wszystko,%s,seriale,0.html' % \
            self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            for link in soup.select('div.title h2 a'):
                series_soup = self.get_soup(self.BASE_URL + '/' + link['href'])
                for episode in series_soup.select('ul.episodes li > a'):
                    season_num, episode_num = self._season_episode_from_url(
                        episode['href']
                    )
                    self._extract_search_links(episode['href'],
                        {'asset_type': ScraperBase.MEDIA_TYPE_TV,
                         'series_season': season_num,
                         'series_episode': episode_num,
                         })


    def _extract_search_links(self, link, kwargs):
        movie_soup = self.get_soup(self.BASE_URL + '/' + link)
        # Grab each lang link, and submit
        lang_box = movie_soup.find('div', 'langs')
        if lang_box:
            for lang_link in lang_box.select('a'):
                kwargs['link_url'] = self.BASE_URL + '/' + lang_link['href']
                self.submit_search_result(**kwargs)
        # Then each format
        format_box =  movie_soup.find('div', 'langs hd_3d')
        if format_box:
            for format_link in format_box.select('a'):
                kwargs['link_url'] = self.BASE_URL + '/' + format_link['href']
                self.submit_search_result(**kwargs)

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for video_link in soup.select('ul.players > li > a'):
            video_soup = self.get_soup(self.BASE_URL + '/' + video_link['href'])
            season_num, episode_num = self._season_episode_from_url(
                video_link['href']
            )

            for iframe in video_soup.select('div#free_player iframe'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_title=self.util.get_page_title(soup),
                                         link_url=iframe['src'],
                                         series_season=season_num,
                                         series_episode=episode_num,
                                         )


class EkinoTVFilm(EkinoTVBase):

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        super(EkinoTVFilm, self).setup()

    BASE_URL = 'http://ekino.tv'

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/szukaj-wszystko,%s,filmy,0.html' % \
            self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            for link in soup.select('div.title h2 a'):
                self._extract_search_links(link['href'],
                    {'asset_type': ScraperBase.MEDIA_TYPE_FILM}),

    def _extract_search_links(self, link, kwargs):
        movie_soup = self.get_soup(self.BASE_URL + '/' + link)
        # Grab each lang link, and submit
        lang_box = movie_soup.find('div', 'langs')
        if lang_box:
            for lang_link in lang_box.select('a'):
                kwargs['link_url'] = self.BASE_URL + '/' + lang_link['href']
                self.submit_search_result(**kwargs)
        # Then each format
        format_box =  movie_soup.find('div', 'langs hd_3d')
        if format_box:
            for format_link in format_box.select('a'):
                kwargs['link_url'] = self.BASE_URL + '/' + format_link['href']
                self.submit_search_result(**kwargs)


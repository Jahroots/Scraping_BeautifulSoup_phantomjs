#coding=utf-8

import re
from base64 import decodestring
from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class WatchFreeTo(SimpleScraperBase, ScraperBase):

    BASE_URL = 'https://www.gowatchfreemovies.com/'
    OTHER_URLS = ['http://www.watchfree.to', 'http://www.gowatchfreemovies.to']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_urls = [self.BASE_URL + '/?keyword={}&search_section=1'.format(self.util.quote(search_term)),
                       self.BASE_URL + '/?keyword={}&search_section=2'.format(self.util.quote(search_term))]
        for search_url in search_urls:
            for soup in self.soup_each([search_url, ]):
                self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(u'No results') >= 0:
            return self.submit_search_no_results()

        next_link = soup.find('a', title='Next Page')

        for result in soup.select('div.text-wrapper a'):
            if result.href[0] == '/':
                self.submit_search_result(
                    link_url=self.BASE_URL + result.href[1:],
                    link_title=result.text
                )
            else:
                self.submit_search_result(
                    link_url=self.BASE_URL + result.href,
                    link_title=result.text
                )

        if next_link and self.can_fetch_next():
            self._parse_search_results(self.get_soup(
                self.BASE_URL + next_link['href']
            ))

    def _parse_parse_page(self, soup):
        episode_num = soup.find('h1').text
        if 'SE' in episode_num:
            season, episode = re.findall('SE(\d+)', episode_num)[0], re.findall('EP(\d+)', episode_num)[0]
            for link in soup.select('td.link_middle strong'):
                movie_link = decodestring(link.find('a')['href'].split('gtfo=')[-1].split('&')[0])
                title = decodestring(link.find('a')['href'].split('gtfo=')[-1].split('title=')[-1])
                if 'offer' not in movie_link:
                    self.submit_parse_result(
                        link_title=title,
                        link_url=movie_link,
                        series_season=season,
                        series_episode=episode,)

        for link in soup.select('td.link_middle strong'):
            movie_link = decodestring(link.find('a')['href'].split('gtfo=')[-1].split('&')[0])
            title = decodestring(link.find('a')['href'].split('gtfo=')[-1].split('title=')[-1])
            if 'offer' not in movie_link:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_title=title,
                                         link_url=movie_link
                                         )

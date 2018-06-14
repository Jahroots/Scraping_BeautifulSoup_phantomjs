# coding=utf-8

import json
import re

import requests

from sandcrawler.scraper import DuckDuckGo, ScraperBase


class BombujEu(DuckDuckGo, ScraperBase):
    BASE_URL = 'http://www.bombuj.eu'
    OTHER_URLS = ['http://serialy.bombuj.eu']
    SINGLE_RESULTS_PAGE = True
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    # def search(self, search_term, media_type, **extra):
    #     self._parse_search_results(
    #         self.post_soup(
    #             self.BASE_URL + '/4154q37rpc4dsvbp.php',
    #             data={
    #                 'queryString': search_term,
    #             }
    #         )
    #     )
    #
    # def _parse_search_results(self, soup):
    #     found = 0
    #     for result in soup.select('div.obrazok a'):
    #         link = result['href']
    #         title = result.text
    #         self.submit_search_result(
    #             link_url=link,
    #             link_title=title,
    #             )
    #         found = 1
    #     if not found:
    #         return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            title = soup.select_one('h1')
            if title:
                title=title.text
                for link in soup.select('.div#hycusajaxwrapper iframe'):
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link['src'],
                                             link_title=title,
                                             )
                for download_link in soup.select('ul#ajaxtabsul li'):
                    movie_soup = self.get_soup(download_link['link'])
                    for link in movie_soup.select('iframe'):
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=link['src'],
                                                 link_title=title,
                                                 )
            if '/ajax.php' in soup._url:
                episodes = soup.select('div.epizody a')
                for episode in episodes:
                    self.parse(episode.href)



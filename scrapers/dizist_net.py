# coding=utf-8

import json
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DizistNet(SimpleScraperBase):
    BASE_URL = 'http://www.dizist1.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]



    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/arsiv/?q={}'.format(search_term)

    def _parse_search_results(self, soup):
        links = soup.select('article h3 a')
        if not links and len(links) == 0:
            return self.submit_search_no_results()
        
        for link in links:
            soup = self.get_soup(self.BASE_URL + link.href)
            episodes = soup.select('div.episode-row a')
            for episode in episodes:
                url = self.BASE_URL + episode.href
                self.submit_search_result(
                    link_url=url,
                    link_title=episode.text,
                )

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = re.findall('(\d+)-sezon', title),\
                              re.findall('(\d+)-bolum', title)

        text = soup.find('script', text=re.compile('"file":"'))
        if text:
            text = text.text.split("JSON.parse('")[1].split("');")[0]
            items = json.loads(text)
            for item in items:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=item['file'],
                    series_season=season,
                    series_episode=episode,
                    link_text=title,
                )

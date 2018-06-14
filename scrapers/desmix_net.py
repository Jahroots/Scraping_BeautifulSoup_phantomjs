# coding=utf-8

import re
import base64
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DesmixNet(SimpleScraperBase):
    BASE_URL = 'https://ddmix.net'
    OTHER_URLS = ['http://desmix.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('a.clip-link'):
            title = result.find_next('p', 'stats').text
            self.submit_search_result(
                link_url=result['href'],
                link_title=title
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for episode_links in soup.select('div.smallTable3'):
            title = episode_links.find('h3').text
            season, episode = self.util.extract_season_episode(index_page_title)
            for episode_link in episode_links.select('div.la34 a') :
                if 'enlacesmix.com' in episode_link['href']:
                    movie_link = base64.decodestring(episode_link['href'].split('/')[-1])
                else:
                    movie_link = episode_link['href']
                self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=movie_link,
                            link_title=title,
                            series_season=season,
                            series_episode=episode
                        )

        for episode_links in soup.select('div.smallTable2'):
            title = soup.find('div', 'titulo').text
            episodes = ''
            try:
                episodes = episode_links.find('div','mirrorsnormales').find_all('div', re.compile('separate.?'))
            except AttributeError:
                pass
            for episode_link in episodes:
                for encoded_link in episode_link['onclick'].split(",'")[-1].split("')")[0].split(','):
                    movie_link = ''.join([chr(int(num)) for num in base64.decodestring(encoded_link).split('-')])
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=title,
                    )

        # for magnet in soup.find_all('a', 'separate3 magnet'):
        #     title = soup.find('div', 'titulo').text
        #     magnet_url = magnet['href']
        #     self.submit_parse_result(
        #         index_page_title=index_page_title,
        #         link_url=magnet_url,
        #         link_title=title,
        #     )

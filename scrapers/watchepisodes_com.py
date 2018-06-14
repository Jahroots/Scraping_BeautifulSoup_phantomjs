# -*- coding: utf-8 -*-
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WatchEpisodes(SimpleScraperBase):
    BASE_URL = 'http://www.watchepisodes4.com'
    OTHER_URLS = [
        'http://www.watchepisodes3.com',
        "http://www.watchepisodes1.to",
        "http://www.watchepisodes.to",
        "http://watchepisodes.com",
        'http://www.watchepisodes1.tv',
        'http://www.watch-episodes.tv',
        "http://www.watchepisodes1.com",
        "http://www.watchepisodes1.net",
                  ]

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

            # self.long_parse = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/ajax_search?q=' + search_term

    def _fetch_no_results_text(self):
        return "Sorry, we could not find the"

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('-----------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        jsn = json.loads(self.get(soup._url).text)
        found = 0
        for serie in jsn.get('series', []):
            soup = self.get_soup(u'{}/{}'.format(self.BASE_URL, serie['seo']))
            for link in soup.select('.el-item a'):
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href,
                )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('.general-right > h2').text[:-7]
        season, episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        for lnk in soup.select('.site-link'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=lnk.attrs['data-actuallink'],
                link_title=title,
                series_season=season,
                series_episode=episode
        )

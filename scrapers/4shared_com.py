# coding=utf-8

import re
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FourSharedCom(SimpleScraperBase):
    BASE_URL = 'https://www.4shared.com'
    OTHER_URLS = ['http://www.4shared.com', 'http://video.4sync.com']

    # WARNING the site changes its interface language according to user's geoIP

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL]+self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type=None, page=0):
        self.start = page
        self.search_term = search_term
        return '{base_url}/web/rest/v1_2/files?query={search_term}&offset={page}&category=2&view=web&limit=12'.format(base_url=self.BASE_URL,
                                                                            search_term=search_term,
                                                                            page=page)

    def _fetch_no_results_text(self):
        return '"totalCount":0'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 12
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        json_text = json.loads(soup.text)
        items = json_text['items']
        for result in items:
            link = 'http:'+result['d1PageUrl']
            self.submit_search_result(
                link_url=link,
                link_title=result['fileName'],
                image=result['thumbnailUrl'],
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        # print soup
        video_url = soup.select_one('video source')
        if video_url:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=video_url['src'],
                link_title=video_url.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        audio_url = soup.select_one('input.jsD1PreviewUrl')
        if audio_url:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=audio_url['value'],
                link_title=audio_url.text,
                series_season=series_season,
                series_episode=series_episode,
            )

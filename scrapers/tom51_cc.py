# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException
import time
import re


class Tom51(SimpleScraperBase):
    BASE_URL = 'http://www.qvodzy.com'
    OTHER_URLS = ['http://www.tom51.cc', 'http://tom51.com', 'http://www.tom551.com']
    # LONG_SEARCH_RESULT_KEYWORD = 'godzilla'
    first = True
    USER_AGENT_MOBILE = True
    USER_AGENT_DESKTOP = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'chi'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.asp'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next = soup.select_one('a.pagelink_a')
        self.log.debug('---------------')
        return next['href'] if next else None

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)

        soup = self.post_soup(search_url, data = {'searchword' : search_term,}
                              )
        if u'时间间隔为300秒' in soup.text:
            time.sleep(301)
            soup = self.post_soup(search_url,  data = {'searchword' : search_term,})

        results = soup.select('li[class="item"] a[class="item-link"]')

        if not results or len(results) == 0:
            self.first = False
            return self.submit_search_no_results()

        self.first = True

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        results = soup.select('li[class="item"] a[class="item-link"]')

        if self.first and (not results or len(results) == 0):
            self.first = False
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url= self.BASE_URL + result.href,
                link_title=result.text,
                image= self.util.find_image_src_or_none(result, 'img')
            )

        next_button = self._fetch_next_button(soup)

        if next_button and self.can_fetch_next():
            soup = self.get_soup(self.BASE_URL + next_button)
            self._parse_search_result_page(soup)



    def _parse_parse_page(self, soup):
            title = soup.select_one('h1').text.strip()
            for link in soup.select('div[class="detail-btn"] a'):
                video_soup = self.get_soup(self.BASE_URL+link['href'])
                video_section = video_soup.select_one('section.video-area script')
                if video_section:
                    video_links_js = self.util.find_urls_in_text(self.get_soup(self.BASE_URL+video_section['src']).text)
                    for video_link_js in video_links_js:
                        if 'cdn' in video_link_js:
                            self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                                     link_url= video_link_js.split('$')[0],
                                                     link_title=title,
                                                     # series_season=season,
                                                     # series_episode=epis.text
                                                     )


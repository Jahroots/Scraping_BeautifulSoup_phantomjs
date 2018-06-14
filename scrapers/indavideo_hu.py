#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class IndavideoHu(SimpleScraperBase):

    BASE_URL = 'http://indavideo.hu'
    OTHER_URLS = ['http://daemon.indapass.hu', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "hun"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.requires_webdriver = True
        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)
        self.proxy_region = 'hun'

    def _fetch_no_results_text(self):
        return u'0 találat'

    def _fetch_search_url(self, search_term, media_type, start=1):
        self.start = start
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/search/text/{}?p_uni={}'.format(search_term.encode('utf-8'), start)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, self.media_type, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('a.title'):
            if 'http://indavideo.hu' in link.href:
                self.submit_search_result(
                    link_title=link.text.strip(),
                    link_url=link.href
                )


    def _parse_parse_page(self, soup):
        title = soup.find('h1', 'videoTitle').text.strip()
        episode = ''
        try:
            episode = re.compile(u'(\d+)\.?\s?rész').search(title).group(1)
        except AttributeError:
            pass
        season = ''
        try:
            episode = re.compile(u'(\d+)\.?\s?évad').search(title).group(1)
        except AttributeError:
            pass
        url =soup.select_one('div#player iframe')
        if url:
            url = url['src']
            if 'advert' not in url:
                if 'http' not in url:
                    url = 'http:'+url
                self.webdriver().get(url)
                soup = self.make_soup(self.webdriver().page_source)
                video_source = soup.select_one('video.video-player')
                if video_source:
                    video_source= video_source['src']
                    self.webdriver().close()
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=video_source,
                                             series_season=season,
                                             series_episode=episode,
                                             )
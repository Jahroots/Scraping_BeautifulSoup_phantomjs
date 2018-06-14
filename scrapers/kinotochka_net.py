# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin
import re
import json

class KinotochkaNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinotochka.club'
    OTHER_URLS = ['http://kinotochka.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.sres-wrap'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img', prefix=self.BASE_URL),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for link in self.util.find_file_in_js(unicode(soup)):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                series_season=series_season,
                series_episode=series_episode,
            )

        # Find
        # "pl":"http://kinotochka.net/pl/cR4ETwBCe1YbTztZMDxaCz8BOzE1_CEVLW3hTBwRWXA::.txt"
        for playlist in re.findall(
            '"pl":"(.*?)"',
            unicode(soup)
        ):
            # This returns json.. but... doesn't.
            body = self.get(
                playlist
            ).content
            for link in self.util.find_file_in_js(body):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TorrenthulkxCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.torrenthulkx.com/'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        raise NotImplementedError("Website removed it's content")
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_ALL)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Unfortunately, site search yielded no results'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#dle-content div.side'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),\
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.mr a'):
            if 'http' in link.text:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        raw_links = None
        try:
            raw_links = self.util.find_urls_in_text(soup.select_one('div.mr div.quote').text)
        except AttributeError:
            pass
        if raw_links:
            for raw_link in raw_links:
                links = map(lambda s: 'http'+s, raw_link.split('http')[1:])
                for link in links:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
# coding=utf-8
import re
from sandcrawler.scraper import FlashVarsMixin
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class KaztubeKz(FlashVarsMixin, SimpleScraperBase):
    BASE_URL = 'https://kaztube.kz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(KaztubeKz, self).get(url, verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/video?q={search_term}&search=&sort=&duration=&added=&page={page}'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return None

    def _parse_search_results(self, soup):
        if not soup.select('a.a'):
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        results = soup.select('a.a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link = soup.select_one('#my-video source')#re.search("""src: \"(.*)\",""", soup.text)
        if link:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )
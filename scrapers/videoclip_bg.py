# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class VideoclipBg(SimpleScraperBase):
    BASE_URL = 'http://www.videoclip.bg'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search?search_query={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Показване на 0-0 от 0 резултати'

    def _fetch_next_button(self, soup):
        next_button = soup.find('ul', 'pagination').find_all('a')[-1]
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.player video'):
            source_link = result.select_one('source')
            if source_link:
                link = 'http:'+source_link['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
            else:
                link = 'http:'+re.search('''"src":"(.*)"}''', unicode(result)).groups()[0]
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

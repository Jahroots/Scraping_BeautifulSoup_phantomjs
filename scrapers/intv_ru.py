# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class IntvRu(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.intv.ru'
    OTHER_URLS = ['http://intv.ru', ]
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    #  search does not work on the website

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.box-header > div')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        div = soup.select_one('div.notavailable')
        if div:
            text = div.find_next('script')
            if text:
                text = text.text
                links = self.util.find_urls_in_text(text)
                for link in links:
                    if 'id=' in link:
                        self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link,
                                link_title=link,
                                series_season=series_season,
                                series_episode=series_episode,
                            )

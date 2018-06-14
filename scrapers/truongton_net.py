# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class TruongtonNet(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://truongton.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.post-message strong')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.post-message pre.alt2')+soup.select('td.alt2 a'):
            links_list = self.util.find_urls_in_text(result.text)
            for link in links_list:
                if 'youtube' in link or 'subscene' in link or 'imbd' in link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        online_sources = soup.find_all(text=u"Xem online")
        if online_sources:
            for online_source in online_sources:
                movie_link = online_source.find_next('a')['href']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=online_source.find_next('a').text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for result in soup.select('a'):
            if 'http' in result.text:
                link = result['href']
                if 'youtube' in link or 'subscene' in link or 'imbd' in link or '/' in link[-1] or 'pic' in link or 'vcheckvirus' in link or len(link)==4:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=result.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )


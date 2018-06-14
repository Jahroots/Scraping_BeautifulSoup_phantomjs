# coding=utf-8
import re
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class VovfNet(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://vovf.net'
    OTHER_URLS = ['http://gameofthrones.vovf.net', 'http://fearthewalkingdead.vovf.net', 'http://vikings.vovf.net',
                  'http://thewalkingdead.vovf.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    LONG_SEARCH_RESULT_KEYWORD = 'viking'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        name_title = soup.select_one('h2')
        season_title = soup.select_one('h3[style="text-align: center;"]')
        if name_title and season_title:
            title = name_title.text + ' ' +season_title.text
            for result in soup.select('div.entry-content a'):
                if 'http' in result.text:
                    episode_title = result.find_previous(text=re.compile('pisode'))
                    series_season, series_episode = self.util.extract_season_episode(title+' '+episode_title)
                    link = result.href
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

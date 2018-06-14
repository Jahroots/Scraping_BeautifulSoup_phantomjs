# coding=utf-8

from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class VerpeliculasonlineComAr(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.verpeliculasonline.com.ar'
    OTHER_URLS = ['http://verpeliculasonline.com.ar/']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.tab iframe'):
            link = result['src']
            if 'http:' not in link:
                link = 'http:'+link
            if 'youtube' in link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )

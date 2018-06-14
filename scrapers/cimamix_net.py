# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleGoogleScraperBase

class CimamixNet(SimpleGoogleScraperBase):
    BASE_URL = 'https://el7l.tv'
    OTHER_URLS = ['https://cimamix.net', 'http://cimamix.net', 'http://cimamix.co']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _parse_parse_page(self, soup):
        watch_link = soup.select_one('a.cliktowatch')
        if watch_link:
            soup = self.get_soup(watch_link.href)

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2.head_title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe in soup.select('iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                series_season=series_season,
                series_episode=series_episode,
            )

        for link in soup.select('div.playerst a'):
            url = link.href
            if not url.startswith('http'):
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                series_season=series_season,
                series_episode=series_episode,
            )

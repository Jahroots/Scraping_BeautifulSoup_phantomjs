# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, SimpleGoogleScraperBase

class Tv543Com(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'http://www.playq.org'
    OTHER_URLS = ['http://www.eyesplay.biz', 'http://www.eyesplay.org/', 'http://www.tv543.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'chi'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(Tv543Com, self).get(
            url,allowed_errors_codes=[404],  **kwargs)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('schedule iframe[width="728"]'):
            movie_link = result['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_link,
                series_season=series_season,
                series_episode=series_episode,
            )
        for embed_link in soup.select('embed'):
            if 'FlashPlayer' in embed_link['src']:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=embed_link['src'],
                link_title=embed_link['src'],
                series_season=series_season,
                series_episode=series_episode,
            )
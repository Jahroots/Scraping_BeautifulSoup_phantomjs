# coding=utf-8
import jsbeautifier
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase


class RlsbbTomindBiz(SimpleGoogleScraperBase):
    BASE_URL = 'http://rlsbb.tomind.biz/'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('the website is out of reach. The domain is for sale')


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        dload_links = soup.select('.postContent a')
        for link in dload_links:
            if link.text not in ('iMDB', 'Torrent Search', 'HOMEPAGE', 'NFO', 'STEAM', 'Homepage'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['href'],
                    link_title=link['href'],
                    series_season=series_season,
                    series_episode=series_episode,
                )

        user_posted_links = soup.select('.messageBox .content a')
        for link in user_posted_links:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_title=link['href'],
                series_season=series_season,
                series_episode=series_episode,
            )
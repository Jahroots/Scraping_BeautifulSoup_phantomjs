# -*- coding: utf-8 -*-

import time
from selenium.webdriver import ActionChains
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleGoogleScraperBase


class CinemaqualidadeCom(SimpleGoogleScraperBase, ScraperBase):
    BASE_URL = 'http://www.cinemaqualidade.to'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return 'https://www.google.com/search?q=' + \
               self.util.quote(search_term) + '+site:www.cinemaqualidade.to'

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        wd = self.webdriver()
        wd.get(soup._url)
        time.sleep(3)
        actionChains = ActionChains(wd)
        links = wd.find_elements_by_xpath('//div[@id="panel_descarga"]//ul[@class="linklist"]//a[@class="link"]/li')
        for link in links:
            actionChains.context_click(link).perform()
            time.sleep(2)
        online_links = wd.find_elements_by_xpath('//div[@id="panel_online"]/ul[@class="linklist"]/div/div/div/li')
        for link in online_links:
            actionChains.context_click(link).perform()
            time.sleep(2)
        for download_link in wd.find_elements_by_xpath('//div[@id="panel_online"]/ul[@class="linklist"]/div/div/div')+wd.find_elements_by_xpath('//div[@id="panel_descarga"]//ul[@class="linklist"]//a[@class="link"]'):
            movie_link = download_link.get_attribute('href')
            if movie_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=movie_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )


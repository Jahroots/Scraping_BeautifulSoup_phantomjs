# coding=utf-8

import time
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SixvhaoCom(SimpleScraperBase):
    BASE_URL = 'http://www.hao6v.com'
    OTHER_URLS = ['http://www.pp63.com','http://www.6vhao.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    PAGE = 1

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'抱歉，没有搜索到您想要的结果'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[href*="page=' + str(self.PAGE) + '"]')
        self.PAGE += 1
        if next_button:
            return self.BASE_URL + next_button['href']
        else:
            return None

    def search(self, search_term, media_type, **extra):
        self.PAGE = 1
        time.sleep(10)
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/e/search/index.php',
                data={
                    'show':'title,smalltext', 'tempid':'1', 'keyboard':self.util.quote(search_term),
                    'tbname':'article', 'x':'25', 'y':'15'
                }
            )
        )

    def _parse_search_results(self, soup):

        if unicode(soup).find(u'没有搜索到相关的内容') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('span.blue14'):
            link = result.select_one('a')
            (season, episode) = self.util.extract_season_episode(link.text)
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                series_season=season,
                series_episode=episode,
            )

        next_button = self._fetch_next_button(soup)

        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button)
            )


    def parse(self, page_url, **kwargs):
        soup = self.make_soup(self.get(page_url).text)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        links_blocks = soup.find(text=re.compile(u'下载地址|¡¾ÏÂÔØµØÖ·¡¿')).find_all_next('table', attrs={'bgcolor': '#0099cc'})
        for links_block in links_blocks:
            for link in links_block.select('a'):
                if 'ed2k' in link.href or 'thunder' in link.href or 'magnet' in link.href or 'ftp' in link.href:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

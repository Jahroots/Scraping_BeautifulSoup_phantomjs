# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Contentchina(SimpleScraperBase):
    BASE_URL = 'http://www.contentchina.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search_{search_term}/'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'抱歉，没有找到'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=re.compile(u'ÏÂÒ»'))
        if next_button:
            return self.BASE_URL+next_button.href
        return None


    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.make_soup(self.get(
                '{base_url}/search_{search_term}/'.format(base_url=self.BASE_URL, search_term=search_term)
            ).text)
        )


    def _parse_search_result_page(self, soup):
        if unicode(soup).find(u'抱歉，没有找到') >= 0:
            return self.submit_search_no_results()
        found=0
        for result in soup.select('div.posterPlaceholder'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('a[name="playLink"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

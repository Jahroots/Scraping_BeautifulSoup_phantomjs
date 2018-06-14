# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class GalaxyclubCn(SimpleScraperBase):
    BASE_URL = 'http://galaxyclub.cn'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'zho'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/BBS/AllPostSearch?Key={search_term}&option=&OrderType=&ParentFId='.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'很抱歉，没有找到与'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.paging a.next')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.list-type01 ul li'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.BSHARE_POP a'):
            if 'http' in result.text:
                link = result.text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for result in soup.select('div.BSHARE_POP span'):
            if 'thunder:' in result.text or 'ed2k:' in result.text:
                link = result.text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class StreameNet(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://streame.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    LONG_SEARCH_RESULT_KEYWORD = 'light'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Domain for sale.')

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        data = None
        try:
            id_num = soup.find('div', 'contentbackag contentbackag2').find('form').find('input', attrs={'name': 'id'})[
                'value']
            fname = soup.find('form').find('input', attrs={'name':'fname'})['value']
            referer = soup.find('form').find('input', attrs={'name':'referer'})['value']
            hash_str = soup.find('form').find('input', attrs={'name':'hash'})['value']
            usr_login = soup.find('form').find('input', attrs={'name':'usr_login'})['value']
            op = soup.find('form').find('input', attrs={'name':'op'})['value']
            data = {'op':op, 'usr_login':usr_login, 'id':id_num, 'fname':fname, 'referer':referer, 'hash':hash_str,
                    'imhuman':'Proceed to video'}
        except AttributeError:
            pass
        if data:
            time.sleep(6)
            post_soup = self.post_soup(soup._url, data=data)
            links = self.util.find_file_in_js(unicode(post_soup))
            for link in links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
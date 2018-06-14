# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json

class AcfunCn(SimpleScraperBase):
    BASE_URL = 'http://www.acfun.cn'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'zho'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE= 'phantomjs'
    PAGE = 1
    TERM = ''
    HAS = False


    def _fetch_search_url(self, search_term, media_type):
        return 'http://search.aixifan.com/search?q={}&isArticle=1&cd=1&sys_name=pc&format=system.searchResult&pageSize=10&pageNo={}&aiCount=3&spCount=3&type=2&isWeb=1&sortField=score&_=1501456829938'.format(search_term, self.PAGE)


    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        return u'http://search.aixifan.com/search?q={}&isArticle=1&cd=1&sys_name=pc&format=system.searchResult&pageSize=10&pageNo={}&aiCount=3&spCount=3&type=2&isWeb=1&sortField=score&_=1491596647601'.format(self.TERM, self.PAGE)

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        data = self.get(search_url).text.replace('system.searchResult=', '')
        data = json.loads(data)
        HAS = False

        self._parse_search_result_page(data)

        next_button = self._fetch_next_button(data)
        if next_button and self.can_fetch_next():
            data = json.loads(self.get(next_button).text.replace('system.searchResult=', ''))
            self._parse_search_result_page(data)



    def _parse_search_result_page(self, data):

        items = ''

        if data['data']['page'].has_key('sp'):
            items = data['data']['page']['sp']
        else:
            items = data['data']['page']['list']

        if (not items or len(items) == 0) and not self.HAS:
            return self.submit_search_no_results()

        self.HAS = True
        for item in items:
            self.submit_search_result(
                link_url=self.BASE_URL + '/a/' + item['contentId'],
                link_title=item['description'],
                image=item['titleImg'],
            )




    def parse(self, parse_url, **extra):
        self.webdriver().get(parse_url)
        soup = self.make_soup(self.webdriver().page_source)
        videos = soup.select('div.unit a.title')

        index_page_title = self.util.get_page_title(soup)

        for video in videos:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= self.BASE_URL + video.href,
                link_title=video.text
            )



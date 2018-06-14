# coding=utf-8

import re
import json, time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin

class VodlockCo(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://vodlock.co'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = 'veep'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(self.__class__, self).setup()
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?op=search&k={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="videobox"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for result in soup.select('div[class="videobox"] a'):
            link = result.href
            if '/category/' not in link:
                self.submit_search_result(
                    link_url=link,
                    link_title=result.text,
                )

    def parse(self, parse_url, **extra):
        wd = self.webdriver()
        wd.get(parse_url)
        time.sleep(20)
        wd.find_element_by_name('imhuman').click()
        time.sleep(6)
        soup = self.make_soup(wd.page_source)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.heading-1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        ip_link = id_num = ''
        ip_link_text = re.search('url\(http://(.*)/i', wd.page_source)
        if ip_link_text:
            ip_link = ip_link_text.groups()[0]
        id_text = re.search('\|mp4\|(\w{60})', soup.text)
        if id_text:
            id_num = id_text.groups()[0]
        if ip_link and id_num:
          link = 'http://{}/{}/v.mp4'.format(ip_link, id_num)
          self.submit_parse_result(
                      index_page_title=index_page_title,
                      link_url=link,
                      link_title=link,
                      series_season=series_season,
                      series_episode=series_episode,
              )
        wd.close()
# coding=utf-8
import json
import time
import re
from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin
from sandcrawler.scraper import SimpleScraperBase


class MechoDownload(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL =  "http://www.mechodownload.com"

    OTHER_URLS = [
        'https://www.mechopirate.com',
        "http://www.mechopirate.com",
        "http://www.mechodownload.com"
    ]

    USERNAME = 'yjalaakr@getairmail.com'
    PASSWORD = 'sands'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    #SINGLE_RESULTS_PAGE = True  # in reality - more

    def setup(self):
        raise NotImplementedError('Deprecated, Website for sale')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def _login(self):
        self.load_session_cookies()


        soup = self.get_soup(self.BASE_URL)
        if 'wmt_secToken' not in soup:

            soup = self.post(self.BASE_URL + '/login/login',
                                  data=dict(login=self.USERNAME, register=0, password=self.PASSWORD,
                                             cookie_check=1, _xfToken='', redirect='/')
                                  )

            self.save_session_cookies()



    def _parse_search_results(self, soup):
        results = soup.select('ol.searchResultsList h3.title a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_url=result['href'],
                                      link_title=result.text
                                      )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_results(soup)

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.get_soup(self.BASE_URL)
        token = soup.select_one('input[name="_xfToken"]')['value']
        self.log.debug(token)
        soup = self.post(self.BASE_URL + '/search/search', data = {'keywords' : search_term, 'users' :'',  'date':'', '_xfToken' : token})

        self._parse_search_results(self.make_soup(soup.text))


    def _fetch_search_url(self, search_term, media_type):
        return (self.BASE_URL + '/index-s={}&ftype={}.html'.format(search_term,
                                                                   4 if media_type == self.MEDIA_TYPE_FILM else 0))

    def _fetch_no_results_text(self):
        return 'Nothing found, sorry'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next >')
        self.log.debug('-----------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def parse(self, parse_url, **extra):
        time.sleep(0.1)
        self.load_session_cookies()
        #self._login()
        soup = self.get_soup(parse_url)
        index_title = self.util.get_page_title(soup)
        title = soup.select_one('.titleBar h1').text
        for block in soup.select('.bbCodeBlock.bbCodeCode pre'):
            for link in self.util.find_urls_in_text(block.text):
                if '*****' in link:
                    m = re.search(r'(?smi)safelinking.*?(http[^\s]+)',block.text)
                    if m:
                        url = m.group(1)
                        m = re.search(r'.+\*\/(.+)',url)
                        if m:
                            url = 'http://safelinking.net/' + m.group(1)
                            self.submit_parse_result(index_page_title=index_title, link_title=title.strip(),
                                                     link_url=url)

                elif 'imdb' not in link and 'tv.com' not in link:
                    self.submit_parse_result(index_page_title=index_title, link_title=title.strip(),
                                             link_url=link)

    def get(self, url, **kwargs):
        return super(MechoDownload, self).get(url, allowed_errors_codes=[403,], **kwargs)

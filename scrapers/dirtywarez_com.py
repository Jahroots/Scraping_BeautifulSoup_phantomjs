# coding=utf-8
import re, time
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase, ScraperBase


class DirtywarezCom(SimpleScraperBase):
    BASE_URL = 'https://dirtywarez.com'
    OTHER_URLS = ['https://forum.dirtywarez.com', 'http://forum.dirtywarez.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, SimpleScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USERNAME = 'Shenclace1946'
    PASSWORD = '4WFI6STMMWQSS'
    #REQUIRES_WEBDRIVER = True
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    PAGE = 0

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL + '/login/login')
        if 'Logout' not in unicode(home_soup):
            soup = self.post(
                self.BASE_URL + '/login/login',
                data={'username': self.USERNAME,
                      'password': self.PASSWORD,
                      'register':0,
                      'cookie_check':1,
                      'redirect': 'https://forum.dirtywarez.com/'
                      }
            )

            self.log.debug(soup.text)


    def _fetch_no_results_text(self):
        return u"No suitable matches were found"

    def search(self, search_term, media_type, **extra):
        self.PAGE = 0
        soup = self.post_soup(self.BASE_URL + '/search.php', data = {'query' : search_term})
        self._parse_search_result_page(soup)

    def _fetch_next_button(self, soup):
        #self.log.debug(soup)
        self.PAGE += 1
        link = soup.select('#pagination a')

        self.log.debug(self.BASE_URL + link[self.PAGE]['href'])
        return self.BASE_URL + link[self.PAGE]['href'] if link else None

    def _parse_search_result_page(self, soup):
        found=0

        for result in soup.select('table td.bgx a[rel="nofollow"]'):
            if 'direct-download' in result.href or 'premium' in result.href or 'crack-serial' in result.href:
                continue
            self.submit_search_result(
                    link_url=result.href,
                    link_title=result.text,
            )

            found=1
        if not found:
            return self.submit_search_no_results()

        url = self._fetch_next_button(soup)
        if url and self.can_fetch_next():
            soup = self.get_soup(url)
            self._parse_search_result_page(soup)

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        iframe = soup.select_one('frame#mainFrame')
        if iframe:
            soup = self.get_soup(iframe['src'])
            codes = soup.select('div.quote')
            for code in codes:
                raw_links= self.util.find_urls_in_text(code.text)
                for raw_link in raw_links:
                    links = raw_link.split('http')
                    for link in links:
                        if not link.startswith('http') and link:
                            link = 'http'+link
                        if link:
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link,
                                link_title=link,
                            )

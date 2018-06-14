# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, DuckDuckGo, CachedCookieSessionsMixin, AntiCaptchaMixin


class ApkforkindlefireCom(DuckDuckGo, AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://apkforkindlefire.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    RECAPKEY = '6LeJhw8UAAAAAGFHg1AQc6rDoMfOsiKCuNP39k3n'



    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def parse(self, parse_url, **extra):
        self.log.warning(parse_url)
        if 'APK' in parse_url or 'down' in parse_url:
            soup = self.get_soup(parse_url)
            title = soup.select_one('h1').text
            index_page_title = self.util.get_page_title(soup)
            a = soup.find('a', text=u'Downloader Engine #1')
            if a:
                url = self.BASE_URL + a['onclick'].split('nhAjax(')[1].replace("'", '').replace(');', '').replace('Step1', 'Step3')
                link = self.post_soup(url).select_one('a')
                if link:
                    self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link.href,
                            link_title=title,

                    )




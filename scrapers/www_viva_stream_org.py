# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin

class WwwVivaStreamOrg(CloudFlareDDOSProtectionMixin, AntiCaptchaMixin,CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.viva-stream.ws'
    OTHERS_URLS = ['http://www.viva-stream.info', 'http://www.viva-stream.co', 'http://www.viva-stream.org']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    RECAPKEY = '6LfBixYUAAAAABhdHynFUIMA_sa4s-XsJvnjtgB0'

    def setup(self):
        super(WwwVivaStreamOrg, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def post(self, url, **kwargs):
        return super(WwwVivaStreamOrg, self).post(url, allowed_errors_codes=[403, ], **kwargs)

    def get(self, url, **kwargs):
        return super(WwwVivaStreamOrg, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'Aucun résultat trouvé'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u"»")
        if next_button:
            return 'http:'+next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(self.BASE_URL)

        if 'Attention Required!' in soup.text:
            self._submit_captcha_solve()

        self.load_session_cookies()

        self._parse_search_result_page(self.get_soup(self._fetch_search_url(search_term, media_type)))

    def _parse_search_result_page(self, soup):
        if self._fetch_no_results_text() in soup.text:
            return self.submit_search_no_results()

        for result in soup.select('div.eTitle a'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        series_season, series_episode = self.util.extract_season_episode(title)
        for body in soup.select('div[class*="box"] iframe'):
            if 'youtube' in body['src']:
                continue
            if len(body['src']) < 1:
                continue
            url = body['src']
            if 'http' not in url:
                url = 'http:' + url
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=body.text,
                series_season=series_season,
                series_episode=series_episode
            )

# coding=utf-8

from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin
from sandcrawler.scraper import SimpleScraperBase, ScraperBase
from sandcrawler.scraper.caching import cacheable


class YesfilmesOrg(CloudFlareDDOSProtectionMixin, SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'http://yesfilmes.org'
    OTHER_URLS = []
    RECAPKEY = '6LfBixYUAAAAABhdHynFUIMA_sa4s-XsJvnjtgB0'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.listagem div.item'):
            link = result.select_one('a')
            if link:
                self.submit_search_result(
                    link_url=link['href'],
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )


    def _fetch_no_results_text(self):
        return u'Nenhum post encontrado'

    def _fetch_next_button(self, soup):
        next = soup.find('a', rel='next')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.content center a'):
            if '/ad/' in link.href:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class SceneSource(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.scenesource.me'
    OTHER_URLS = ['http://scenesource.me', ]
    SEARCH_TERM = ''

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '/?s={}'.format(self.SEARCH_TERM)

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        super(SceneSource, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('h2 a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'Emptyness...'

    def _fetch_next_button(self, soup):
        next = soup.select_one('a.nextpostslink')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.content h2').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.comment.clear a') + soup.select('.comm_content a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

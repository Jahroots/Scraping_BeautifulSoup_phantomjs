# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin, CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin


class Year2013zone(OpenSearchMixin, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.2013zone.com'
    OTHER_URLS = ['http://2013zone.com', ]
    RECAPKEY = '6LfBixYUAAAAABhdHynFUIMA_sa4s-XsJvnjtgB0'
    LONG_SEARCH_RESULT_KEYWORD = '2017'

    SINGLE_RESULTS_PAGE = True


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

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'
        # self.media_type_to_category = 'film 0, tv 0'

    def _parse_search_result_page(self, soup):
        results = soup.select('#dle-content td.a_block_22 strong a')
        found = False
        for link in results:
            found = True
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.ntitle').text
        season, episode = self.util.extract_season_episode(title)

        found = False

        for txt in soup.select('.quote') + soup.select('.quote div'):
            for link in txt.contents:

                try:
                    if link and unicode(link).strip().startswith('http'):
                        if len(link.split('http')) > 2:
                            for url in self.util.find_urls_in_text(link):
                                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                         link_url=url,
                                                         link_title=title,
                                                         series_season=season,
                                                         series_episode=episode
                                                         )
                            found = True
                        else:

                            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                     link_url=link,
                                                     link_title=title,
                                                     series_season=season,
                                                     series_episode=episode
                                                     )
                            found = True
                except Exception as e:
                    self.log.exception(e)

        for link in soup.select('.quote div a'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
            found = True

        if not found:
            for url in self.util.find_urls_in_text(soup.select_one('#dle-content').text):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

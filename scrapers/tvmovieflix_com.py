# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin, OpenSearchMixin
from sandcrawler.scraper import SimpleScraperBase, CachedCookieSessionsMixin


class TVmovieFlix(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin,   SimpleScraperBase):
    BASE_URL = 'http://tvmovieflix.com'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        #raise NotImplementedError('The website has bad gateway error')
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        #self._request_size_limit = (1024 * 1024 * 60)  # Bytes

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?menu=search&query=' + search_term

    def _parse_search_results(self, soup):
        results = soup.select('div.item a')
        if not results:
            self.submit_search_no_results()

        for res in results:
            self.submit_search_result(
                link_title=res.text.strip(),
                link_url=res.href
            )

    def _fetch_no_results_text(self):
        return u'Unfortunately we couldn\'t find anything with the search term you entered'

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('span.article__title h1').text
        season, episode = self.util.extract_season_episode(title)

        links = soup.select('div.host_box a[href*="/m/"]')
        for link in links:
            soup = self.get_soup(link.href)
            iframe = soup.select_one('iframe')
            if iframe and iframe.has_attr('src'):
                self.submit_parse_result(index_page_title= index_page_title,
                                     link_url=iframe['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )



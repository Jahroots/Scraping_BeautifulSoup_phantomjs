# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class RdlinksCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.rdlinks.xyz'
    OTHER_URLS = ['https://www.rdlinks.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    USER_NAME = 'Beekh1949'
    PASSWORD = 'Vei2Iwoh2A'
    EMAIL = 'rogerljohnson@teleworm.us'
    WEBDRIVER_TYPE = 'phantomjs'
    REQUIRES_WEBDRIVER = True


    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(self.BASE_URL)
        token = soup.select_one('input[name="_xfToken"]')['value']

        soup = self.post_soup(self.BASE_URL + '/search/search', data = {'_xfToken': token, 'keywords': search_term, 'c[users]':''},
                         )


        if self._fetch_no_results_text() in unicode(soup):
            return self.submit_search_no_results()

        self._parse_search_results(soup)


    def _fetch_no_results_text(self):
        return u'No results found.'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text= u'Next')
        if next_button:
            return '{}/{}'.format(self.BASE_URL, next_button.href)
        return None

    def _parse_search_results(self, soup):
        results = soup.select('div.p-body-pageContent ol.block-body h3')
        if not results or len(results) == 0:
          return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            if not link:
                continue
            self.submit_search_result(
                link_url=self.BASE_URL+'/'+link.href,
                link_title=result.text,
            )
        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            self._parse_search_results(self.get_soup(next_button)
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for bbcode in soup.select('blockquote a'):
            if 'http' in bbcode.text:
                if 'imbd' in bbcode.href:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=bbcode.href,
                    link_title=bbcode.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for bbcode in soup.select('pre.bbCodeCode'):
            for link in self.util.find_urls_in_text(bbcode.text):
                if 'imbd' in bbcode.href:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

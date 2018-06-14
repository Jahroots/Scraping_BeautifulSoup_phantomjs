#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper.extras import VBulletinMixin


class InWarezOrg(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.inwarez.org'
    USERNAME = 'Nowbel1966'
    PASSWORD = 'DevilForum1'
    LONG_SEARCH_RESULT_KEYWORD = '2015'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return 'Sorry - no matches.'

    def _fetch_next_button(self, soup):
        links = soup.select('span.prev_next a')
        for link in links:
            if link.find('img', {'alt': 'Next'}):
                return self.BASE_URL + '/' + link['href']
        return None

    #def get(self, url, **kwargs):
    #    return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def search(self, search_term, media_type, **extra):
        home_soup = self.get_soup(self.BASE_URL)
        security_token = home_soup.find(
            'input', {'name': 'securitytoken'})['value']
        print(security_token)
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data = {
                    'securitytoken': security_token,
                    'do': 'process',
                    'q': search_term,
                    }
            )
        )

    def _parse_search_result_page(self, soup):
        # XXX not getting season/episode as it's not consistent.
        for result in soup.select('li.imodselector'):
            link = result.find('a', 'title')
            asset_type = None
            forum_link = result.find('a', {'href': re.compile('^forumdisplay')})
            if forum_link:
                if forum_link.text == 'TV Shows':
                    asset_type = ScraperBase.MEDIA_TYPE_TV
                elif forum_link.text == 'Full Movies':
                    asset_type = ScraperBase.MEDIA_TYPE_FILM
                elif forum_link.text == 'Video Games':
                    asset_type = ScraperBase.MEDIA_TYPE_GAME
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
                asset_type=asset_type,
            )

    def _parse_parse_page(self, soup):
        # Convention is to put links as plain text in <pre class="bbcode_code"
        # So find them, then find anything that does looks like a link and
        # isn't imdb.
        for textblock in soup.select('div.content'):
            for link in self.util.find_urls_in_text(unicode(textblock)):
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link
                )


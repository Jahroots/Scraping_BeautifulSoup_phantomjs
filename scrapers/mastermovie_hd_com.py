# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import ScraperFetchException


class MasterMovieHDCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.mastermovie-hd.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self._request_connect_timeout = 300
        self._request_response_timeout = 600

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
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        if soup.select('.pagination .inactive'):
            curr_page = 1
            if '/page/' in soup._url:
                curr_page = int(soup._url.split('/')[4])
            max_page = int(soup.select('.pagination .inactive')[-1].text)
            if curr_page < max_page:
                self.log.debug('------------------------')
                return self.BASE_URL + '/page/' + str(curr_page + 1) + '/?s=' + soup._url.split('?s=')[1]

    def _extract_season_episode(self, text):
        match = re.search('season(\d+)-ep(\d+)', text)
        if match:
            return match.groups()
        return None, None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.item')

        if not results:
            self.submit_search_no_results()

        for result in results:
            link = result.select_one('div.item-content header h2 a')
            # image = None
            # img = result.find('img', 'wp-post-image')
            # if img:
            #     image = img['src']
            season, episode = self._extract_season_episode(link['href'])
            # print result
            if link:
                try:
                    self.submit_search_result(
                        link_url=link['href'],
                        link_title=link.text,
                        # image=image,
                        series_season=season,
                        series_episode=episode,
                    )
                except Exception as e:
                    # self.log.error(repr(locals()))
                    self.log.exception(e)

    def parse(self, parse_url, **extra):
        season, episode = self._extract_season_episode(parse_url)

        soup = self.get_soup(parse_url)
        iframes = soup.select('#accordion iframe')

        for iframe in iframes:
            self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=iframe['src'],
                        series_season=season,
                        series_episode=episode,
            )

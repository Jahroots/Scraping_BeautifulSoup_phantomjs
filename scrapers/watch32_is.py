# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class Watch32_is(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://watch32.is'
    TRELLO_ID = '5aQz2Leq'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'
        self._request_connect_timeout = 300
        self._request_response_timeout = 300

    def get(self, url, **kwargs):
        return super(Watch32_is, self).get(url, allowed_errors_codes=[524], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        self.media_type = media_type
        return self.BASE_URL + '/search-movies/{}.html'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'No Results'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        if soup.select('.thumbcontent a.title'):
            for result in soup.find_all('a', {'class': 'title'}):
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text.strip()
                )
        else:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        if not soup:
            self.log.warning('Page not loaded.')
            return
        title = soup.select_one('#tit_player span').text
        season, episode = self.util.extract_season_episode(title)

        for dl in soup.select('.server_play a'):
            dl_soup = self.get_soup(dl['href'])
            for ifr in dl_soup.find_all('iframe'):
                if not ifr['src'].startswith('http://www.facebook.com'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=ifr['src'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

# coding=utf-8

import base64
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, AntiCaptchaMixin
from sandcrawler.scraper import CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable



class TvOnlineTw(SimpleScraperBase, CachedCookieSessionsMixin, AntiCaptchaMixin):
    BASE_URL = 'https://opentuner.is'
    OTHER_URLS = ['http://opentuner.is', 'http://tvonline.tw']
    LONG_SEARCH_RESULT_KEYWORD = 'mother'
    SINGLE_RESULTS_PAGE = True
    RECAPKEY = '6LfDFRgUAAAAAAzPdhZK8tR0Z5C4Y4pZGWgCRtIh'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return 'Sorry there are no TV Shows found like that'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        return None

    def get_links(self, url):
        self.load_session_cookies()
        soup = self.get_soup(url)
        if soup.select('div.g-recaptcha'):
            soup = self.post_soup(
                url,
                data={
                    'g-recaptcha-response': self.get_recaptcha_token(), 'submit': 'SUBMIT'
                }
            )
            self.save_session_cookies()
        results = []
        for result in soup.select('div.found ul li a'):
            results.append(dict(
                link_url=result['href'],
                link_title=result.text,
            ))
        return results


    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        found=0
        for result in self.get_links(search_url):

            self.submit_search_result(
                **result
            )
            show_soup = self.get_soup(self.BASE_URL + '/' + result['link_url'])
            for season in show_soup.select('div.Season'):
                series_season = self.util.find_numeric(season.find('h3').text)
                for episode in season.select('ul li a'):
                    srch = re.search('Episode (\d+)', episode.text)
                    series_episode = None
                    if srch:
                        series_episode = srch.group(1)
                    self.submit_search_result(
                        link_url=episode['href'],
                        link_title=result.text + ' ' + episode.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # episodes
        for epi_link in soup.select('.Season ul li a'):
            epi_soup = self.get_soup(epi_link.href)
            for link in epi_soup.select('.playing_button a'):
                href = link.href
                if href.startswith('/stream.php?'):
                    title, season, serie, url = base64.decodestring(
                        "/stream.php?U2lnbmlmaWNhbnQgTW90aGVyICgyMDE1KSYmMSYmNSYmaHR0cDovL21pZ2h0eXVwbG9hZC5jb20vcGhjMmdoMzd6a2hhL1NpZ25pZmljYW50Lk1vdGhlci5TMDFFMDUuSERUVi54MjY0LUtJTExFUlMubXA0Lmh0bWw="[
                        12:]).split('&&')
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_title=title,
                                             link_url=url,
                                             series_season=season,
                                             series_episode=serie,
                                             )
        # legacy code
        for link in soup.select('ul#linkname_nav li a'):
            # A bunch of escaped chars here.  Escape the escapes. :D
            srch = re.search("go_to\(\d*,\\'(.*)\\'\)", link['onclick'])
            if srch:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=srch.group(1),
                                         )

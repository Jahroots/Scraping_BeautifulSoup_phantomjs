# -*- coding: utf-8 -*-
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperAuthException
from sandcrawler.scraper.extras import CachedCookieSessionsMixin
import time

class BalkandownloadOrg(SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'http://www.balkandownload.org'

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'
    USERNAME = 'Fortiough'
    PASSWORD = 'aix7Ahc4oh'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(BalkandownloadOrg, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL + '/index.php?app=core&module=global&section=login')
        if 'Sign Out' not in unicode(home_soup):
            self.log.debug('Logging in...')
            security_token = home_soup.find(
                'input', {'name': 'auth_key'})['value']
            self.post(self.BASE_URL + '/index.php?app=core&module=global&section=login&do=process',
                                     data={
                                         'ips_username': self.USERNAME,
                                         'ips_password': self.PASSWORD,
                                         'auth_key': security_token,
                                         'rememberMe': '1',
                                         'referer': 'http://www.balkandownload.org/members/'
                                     }
                                     )

    def _fetch_no_results_text(self):
        return u'No results found for '

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _login_success_string(self):
        return u'Sign Out'

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        self._login()
        soup = self.get_soup(self.BASE_URL + (
            '/index.php?app=core&module=search&do=search&andor_type=&search_app_filters[forums][sortKey]=date&search_app_filters[forums][sortKey]=date&search_term={}&search_app=forums&st=0').format(
            self.util.quote(search_term)))
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('td h4 a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text
            )

    def parse(self, parse_url, **extra):
        time.sleep(0.1)
        self._login()
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        auth_key = soup.select_one('form[id*="ips_fastReplyForm"] input[name="auth_key"]')['value']
        tid = soup.select_one('form[id*="ips_fastReplyForm"] input[name="t"]')['value']
        fid = soup.select_one('form[id*="ips_fastReplyForm"] input[name="f"]')['value']
        pid = soup.select_one('li.ajax_thanks a')
        if pid:
            pid = soup.select_one('li.ajax_thanks a').href.split("( '")[-1].split("' )")[0]
            data = {'md5check':auth_key, 'pid':pid, 'tid':tid, 'fid':fid}
            post_link = 'http://www.balkandownload.org/index.php?s=81a36fca30df157c0f1821c48332904f&app=forums&module=ajax&section=stats&do=ajaxThanks'
            links = self.util.find_urls_in_text(json.loads(self.post_soup(post_link, data=data).text)['post'])
            for link in links:
                if 'imbd' not in link:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=link,
                                             series_season=series_season,
                                             series_episode=series_episode
                                             )
        else:
            for link_text in soup.select('pre.prettyprint'):
                for link in self.util.find_urls_in_text(link_text.text):
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=link,
                                             series_season=series_season,
                                             series_episode=series_episode
                                             )


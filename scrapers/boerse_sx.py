#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperAuthException, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper.extras import VBulletinMixin


class BoerseSx(CloudFlareDDOSProtectionMixin, SimpleScraperBase, VBulletinMixin):
    BASE_URL = 'http://www.boerse.sx'
    USERNAME = 'Mustoom'
    PASSWORD = 'eip0iu7N'
    EMAIL = 'davidwechols@dayrep.com'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ger"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return u'Deine Suchanfrage erzielte keine Treffer'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='›')
        return self.BASE_URL + '/' + link['href'] if link else None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _login_success_string(self):
        return u'Danke'

    def _is_valid_login(self, content):
        if unicode(content, errors='ignore').find(self._login_success_string()) == -1:
            raise ScraperAuthException('Failed to login to VBulletin')
        return True

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        self._login()
        home_soup = self.get_soup('http://www.boerse.sx/boerse/videoboerse/')
        security_token = home_soup.find(
            'input', {'name': 'securitytoken'})['value']
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data = {
                    'securitytoken': security_token,
                    'do': 'process',
                    'forumchoice[]':'30',
                    'childforums':'1',
                    'q': search_term,
                    }
            )
        )

    def _parse_search_result_page(self, soup):
        for result in soup.select('table#threadslist tr')[2:-1]:
            link = result.find('a', attrs={'id': re.compile('thread_title')})
            if not link:
                continue
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link.href,
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        self._login()
        for spoiler_link in soup.select('div.body-spoiler div a'):
            if 'imdb.com' in spoiler_link['href'] or 'email-protection' in spoiler_link['href']:
                continue
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=spoiler_link['href']
                )
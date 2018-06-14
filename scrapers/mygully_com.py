#coding=utf-8

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sandcrawler.scraper import ScraperAuthException
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase
import time


class MyGullyCom(CloudFlareDDOSProtectionMixin, ScraperBase):

    BASE_URL = 'http://mygully.com'
    USERNAME = 'Alighway'
    PASSWORD = 'shahJeeXu3bae'
    EMAIL = 'LawrenceIOConnor@rhyta.com'

    LONG_SEARCH_RESULT_KEYWORD = 'mother'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "deu"

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

    def _login(self):
        wd = self.webdriver()
        wd.get(self.BASE_URL)

        try:
            username = wd.find_element_by_name('vb_login_username')
        except NoSuchElementException:
            # We may be an already logged in session... lets say so.
            return
        username.clear()
        username.send_keys(
            self.USERNAME
        )
        password = wd.find_element_by_name('vb_login_password')
        password.clear()
        password.send_keys(
            self.PASSWORD)

        # XXX don't make username Anmelden :|
        wd.find_element_by_xpath("//input[@value='Anmelden']").click()

        time.sleep(10)
        while wd.page_source.find(
                u'Kontrollzentrum'
        ) >= 0:


            try:
                username = wd.find_element_by_name('vb_login_username')
            except NoSuchElementException:
                # We may be an already logged in session... lets say so.
                return
            username.clear()
            username.send_keys(
                self.USERNAME
            )
            password = wd.find_element_by_name('vb_login_password')
            password.clear()
            password.send_keys(
                self.PASSWORD)

        # XXX don't make username Anmelden :|
            wd.find_element_by_xpath("//input[@value='Anmelden']").click()
            time.sleep(5)
        if wd.page_source.find(
            u'Du hast einen falschen Benutzernamen oder ein falsches'
        ) >= 0:
            raise ScraperAuthException('Failed login with %s / %s')
        # XXX Kind of ugly, but can't work out another way around it.
        # Then wait until we can see the control panel link; basically
        # until it's redirect.  Otherwise subsequent GETs don't seem
        # to go through.

        # WebDriverWait(wd, 10).until(
        #     EC.presence_of_element_located(
        #         (By.LINK_TEXT, 'Kontrollzentrum')
        #     )
        # )

    def _fetch_no_results_text(self):
        return u'Bitte versuche es mit anderen Suchbegriffen'

    def search(self, search_term, media_type, **extra):
        self._login()
        # Get a base page
        wd = self.webdriver()
        wd.get(self.BASE_URL + '/search.php?do=process')

        if unicode(wd.page_source).find('Du bist nicht angemeldet oder du hast keine') > 0 or unicode(wd.page_source).find('Registrieren') > 0:
            self._login()
        wd.find_element_by_css_selector(
            'form#searchform input[name=query]').send_keys(search_term)
        wd.find_element_by_name('dosearch').click()

        time.sleep(15)
        # element = WebDriverWait(wd, 10).until(
        #     EC.presence_of_element_located((By.T, "myDynamicElement"))
        # )
        if wd.page_source.find(
            u'Bitte versuche es mit anderen Suchbegriffen') >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(self.make_soup(wd.page_source))

    def _parse_search_result_page(self, soup):
        for result in soup.find_all('a', style='font-weight:bold'):
            href = result['href']
            link_title = result.text
            season, episode = self.util.extract_season_episode(link_title)
            self.submit_search_result(
                link_url=href,
                link_title=link_title,
                series_season=season,
                series_episode=episode,
            )

        next_link = soup.find('a', text=u'>')
        # print next_link['href']
        if next_link and self.can_fetch_next():
            self._parse_search_result_page(self.get_soup(
                self.BASE_URL + '/' + next_link['href']
            ))


    # def _parse_search_result_page(self):
        # wd = self.webdriver()
        # for link in wd.find_elements_by_xpath(
        #     "//a[starts-with(@id, 'thread_title')]"):
        #
        #     href = link.get_attribute('href')
        #     link_title = link.text
        #     season, episode = self.util.extract_season_episode(link_title)
        #     self.submit_search_result(
        #         link_url=href,
        #         link_title=link_title,
        #         series_season=season,
        #         series_episode=episode,
        #     )
        #
        # if self.can_fetch_next():
        #     try:
        #         letztelinks = wd.find_elements_by_link_text(
        #             '>')
        #     except NoSuchElementException:
        #         pass
        #     else:
        #         next_link = letztelinks[-1]
        #         next_link.click()
        #         self._parse_search_result_page()

    def parse(self, parse_url, **extra):
        self._login()
        wd = self.webdriver()
        # Open the page.
        wd.get(parse_url)
        # Open all spoilers.
        for spoiler in wd.find_elements_by_css_selector(
            'div.pre-spoiler input'):
            spoiler.click()
        index_page_title = wd.find_element_by_tag_name(
            'title').get_attribute('innerHTML')
        # And find all links
        for post in wd.find_elements_by_xpath(
            "//div[starts-with(@id, 'post_message')]"):
            title, season, episode = None, None, None
            try:
                post_title = post.find_element_by_tag_name('b')
            except NoSuchElementException:
                pass
            else:
                title = post_title.text
                season, episode = self.util.extract_season_episode(title)
            for link in post.find_elements_by_tag_name('a'):
                try:
                    href = link.get_attribute('href')
                except:
                    continue
                if '.jpg' in href or '.png' in href:
                    continue
                elif not href.startswith(self.BASE_URL):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=href,
                        link_title=link.text,  # or page title?
                        series_season=season,
                        series_episode=episode,
                        )



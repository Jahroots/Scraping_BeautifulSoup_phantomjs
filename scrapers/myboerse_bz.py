# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase
from sandcrawler.scraper.caching import cacheable
from sandcrawler.scraper.extras import VBulletinMixin, ScraperAuthException, CloudFlareDDOSProtectionMixin
import random
import hashlib


class MyBoerseBz(CloudFlareDDOSProtectionMixin, SimpleScraperBase, ScraperAuthException):
    BASE_URL = 'http://myboerse.bz'
    USERNAME_LIST = [{'user':'Oripsensfuld', 'password':'naa0iaGhek'}, {'user':'Wifirs','password':'aemae9gi1Lo'},
                     {'user':'Hichatell42','password':'eeSoonohg8'}, {'user':'Thensiong','password':'ahte4noYep'},
                     {'user':'Sainest','password':'au2bi9Okee1'}, {'user':'Lery1964','password':'Laiquooz9soh'},
                     {'user':'Whoulet', 'password':'vah7ohNgoo6'},{'user':'Witive','password':'oa6eefeNgu'},
                     {'user':'Bowerelea1997','password':'Fegh1joka5n'}, {'user':'Fingthily', 'password':'ze6aiv8Goh'},
                     {'user':'Conamill', 'password':'AezaiTei4ei'},{'user':'Wituarmay', 'password':'zahJee9ai'},
                     {'user':'Mooked', 'password':'shaoJai7no'},{'user':'Exclown75','password':'aiyie4xie1Th'},
                     {'user':'Thiptin1940', 'password':'Chiev2ohxoh'}]
    USER_CREDENTIALS = random.choice(USERNAME_LIST)
    USERNAME = USER_CREDENTIALS['user']
    PASSWORD = USER_CREDENTIALS['password']
    EMAIL = 'JamesRColvin@jourrapide.com'

    ALLOW_GUEST_TOKEN = False
    SECURITY_TOKEN_NAME = 'securitytoken'

    LONG_SEARCH_RESULT_KEYWORD = '720p BluRay'



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

    def _fetch_next_button(self, soup):
        link = soup.find('a', {'rel': 'next'})
        if link:
            return self.BASE_URL + '/' + link['href']

    def _login_success_string(self):
        return 'Danke'

    def _fetch_no_results_text(self):
        return u'Deine Suchanfrage erzielte keine Treffer'

    @cacheable()
    def list_video_subforums(self):
        return [forum.href for forum in
                self.get_soup(self.BASE_URL + '/forum39/').select('.forumtitle a')]


    def _login(self):
        home_soup = self.get_soup(self.BASE_URL + '/login.php?do=login')

        if 'Abmelden' not in unicode(home_soup):
            USER_CREDENTIALS = random.choice(self.USERNAME_LIST)
            username = USER_CREDENTIALS['user']
            PASSWORD = USER_CREDENTIALS['password']
            md5_password = hashlib.md5(PASSWORD).hexdigest()
            security_token = home_soup.find(
                'input', {'name': 'securitytoken'})['value']
            self.post(self.BASE_URL + '/login.php?do=login',
                                     data={
                                            'vb_login_username': username,
                                            'vb_login_password': '',
                                            'vb_login_password_hint': '',
                                            'securitytoken': security_token,
                                            'do': 'login',
                                            'vb_login_md5password': md5_password,
                                            'vb_login_md5password_utf': md5_password,
                                     }
                                     )


    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        self._login()
        home_soup = self.get_soup(self.BASE_URL)
        security_token = home_soup.find(
            'input', {'name': 'securitytoken'})['value']
        soup = self.post_soup(
            self.BASE_URL + '/search.php?do=process',
            data={
                'securitytoken': security_token,
                'do': 'process',
                'query': search_term,
            }
        )
        while unicode(soup).find(
                'aber du kannst nur alle 20 Sekunden eine neue Suche starten') >= 0:
            self.get(self.BASE_URL)
            self._login()
            security_token = home_soup.find(
                'input', {'name': 'securitytoken'})['value']
            soup = self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data={
                    'securitytoken': security_token,
                    'do': 'process',
                    'query': search_term,
                }
            )


        self._parse_search_results(soup)


    def _parse_search_result_page(self, soup):

        for page_link in soup.select('h3.searchtitle a.title'):
            page_link_soup = self.get_soup(page_link['href'])
            if any(nav.text == 'Videoboerse' for nav in
                   page_link_soup.select('.navbit a')):  # or - use list_video_subforums()
                self.submit_search_result(
                    link_url=page_link['href'],
                    link_title=page_link.text,
                )


    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        for post in soup.select('blockquote.postcontent'):
            # Try and find a bold'nd element for a title.
            link_title, season, episode = None, None, None

            boldned = post.find('b')
            if boldned:
                link_title = boldned.text
                season, episode = self.util.extract_season_episode(
                    link_title)

            for link in post.select('a'):
                if 'href' in link.attrs:
                    this_link_title = link_title or link.text
                    if 'php?u' not in link.href and 'imbd' not in link.href:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link['href'],
                                                 link_title=this_link_title.strip(),
                                                 series_season=season,
                                                 series_episode=episode,
                                                 )

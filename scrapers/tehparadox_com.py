# -*- coding: utf-8 -*-
import time
import random

from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin, CachedCookieSessionsMixin


class TehParadoxCom(SimpleScraperBase, VBulletinMixin, CachedCookieSessionsMixin):
    BASE_URL = 'http://tehparadox.com/forum'
    REGISTER_URL = 'http://tehparadox.com'

    USERNAME = 'sandcrawler'
    PASSWORD = 'sandcrawler1'

    LONG_SEARCH_RESULT_KEYWORD = 'ascension'

    GET_ATTEMPTS = 1

    def setup(self):
        raise NotImplementedError('Deprecated. Website unreachable.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        # this one is quirky.
        # we need base_url to be '/forum' for use with the vbulleting mixin.
        # but we need base url to not be for correct registration.

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.REGISTER_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.REGISTER_URL)

        # This one times out a lot...
        self.GET_ATTEMPTS = 2


    def _fetch_no_results_text(self):
        return 'Sorry - no matches.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next", text='>')
        return self.BASE_URL + '/' + link['href'] if link else  None

    def search(self, search_term, media_type, **extra):
        self.load_session_cookies()

        home_page = self.get(self.BASE_URL + '/').content
        if '/forum/login.php?do=login' in unicode(home_page):
            self._login()
            self.save_session_cookies()

            home_page = self.get(self.BASE_URL + '/').content

        home_soup = self.make_soup(home_page)

        security_token = home_soup.find(
            'input', {'name': 'securitytoken'})['value']


        tries = 0
        while tries < 5:
            tries += 1
            page_results =  self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data={
                    'securitytoken': security_token,
                    'do': 'process',
                    'q': search_term,
                }
            )
            if 'This forum requires that you wait' in str(page_results):
                time_to_wait = int(
                    str(page_results).split('again in ')[1].split(' seconds')[
                        0]) + random.randint(2, 15)
                self.log.warning('Got wait message - waiting %s', time_to_wait)
                time.sleep(time_to_wait)
            elif 'The server is too busy at the moment. Please try again later.' in str(
                    page_results):
                raise ScraperParseException(
                    'Got "The server is too busy at the moment. Please try again later."')
            else:
                self._parse_results_page(page_results)
                while self.can_fetch_next():
                    next_page = page_results.select_one('a[rel="next"]')
                    if next_page:
                        page_results = self.get_soup(
                            self.BASE_URL + '/' + next_page.href,
                        )
                        self._parse_results_page(page_results)
                    else:
                        break


    def _parse_results_page(self, page_results):

        results = [a for a in page_results.find_all('a', rel="nofollow")
                   if a.attrs.get('id', '').startswith("thread_title")]
        if not results:
            self.submit_search_no_results()

        for link in results:
            asset_type = link.parent.parent.parent.find_all('td')[
                -1].find('a').text
            if 'TV Shows' in asset_type:
                asset_type = ScraperBase.MEDIA_TYPE_TV
            elif ('Film & Television' in asset_type) or (
                'Movies' in asset_type) or ('HD' in asset_type) or (
                'DVDR' in asset_type):
                asset_type = ScraperBase.MEDIA_TYPE_FILM
            elif 'Games' in asset_type:
                asset_type = ScraperBase.MEDIA_TYPE_GAME
            else:
                asset_type = None

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
                asset_type=asset_type,
            )


    def parse(self, parse_url, **extra):
        tries = 0
        while tries < 10:
            tries += 1
            self.load_session_cookies()
            soup = self.get_soup(parse_url)
            if "You are not logged in or you do not have permission to access this page" in unicode(
                    soup) or "http://cdn.tehparadox.com/forum/images/guests.png" in unicode(
                soup) or "Forgot?" in unicode(soup):
                time.sleep(5)
                self._login()
            else:
                if tries > 1:
                    self.save_session_cookies()
                break
        exist_links = set()
        for post in soup.select_one('#posts'):  # .find_all('pre'):
            # for link in self.util.find_urls_in_text(unicode(post.text)):
            for link in self.util.find_urls_in_text(unicode(post), skip_images=True):
                if 'tehparadox.com' not in link:
                    exist_links.add(link)
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link, link_text=soup.h1.text.strip()
                                             )
        for box in soup.select('pre.alt2'):
            for link in self.util.find_urls_in_text(box.text, skip_images=True):
                if 'tehparadox.com' not in link:
                    if link not in exist_links:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link, link_text=soup.h1.text.strip()
                                                 )

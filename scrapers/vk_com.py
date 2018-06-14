# coding=utf-8

import urlparse
import re
import json
import time
import random

import redis_cache
import vk

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper import ScraperParseException, ScraperAuthException
from sandcrawler.scraper.caching import cache

#  some can be borrowed from https://github.com/soimort/you-get/blob/develop/src/you_get/extractors/vk.py

class VKCom(SimpleScraperBase):
    BASE_URL = 'https://api.vk.com'
    OTHER_URLS = ['https://vk.com', ]

    USERNAME = 'victoraruffin@gmail.com'
    PASSWORD = 'loyalty7redmoon%'
    CACHE_KEY = 'VK_API_ACCESS_TOKEN'

    # Documentation says this is 200, but I can only get 166 at a time.
    # eh.
    MAX_COUNT = 166

    LONG_SEARCH_RESULT_KEYWORD = 'dvd'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.long_parse = True

        for url in (self.BASE_URL, 'https://vk.com'):
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _get_access_token(self):

        try:
            access_token = cache.get_pickle(self.CACHE_KEY)
        except (redis_cache.ExpiredKeyException,
                redis_cache.CacheMissException):
            pass
        else:
            if access_token:
                return access_token
        self.log.info('Fetching new VK access_token')

        token = self._fetch_new_access_token()

        cache.store_pickle(self.CACHE_KEY, token)

        return token

    def _clear_access_token(self):
        cache.invalidate(self.CACHE_KEY)

    def _fetch_new_access_token(self):

        # Get the auth url
        url = 'https://oauth.vk.com/authorize?client_id=' \
              '4583728&scope=video&redirect_uri=http://api.vk.com/blank.html' \
              '&response_type=token&v=5.25'
        response = self.get(url)
        # Bs4 is being a hog here - it's not findign the form on a full
        # parse of the page... suck out the form manually and soup it.
        start_index = response.content.find('<form')
        end_index = response.content.find('</form>')
        if start_index < 0 or end_index < 0:
            raise ScraperParseException('Could not find form.')
        login_page_soup = self.make_soup(response.content[start_index:end_index + 7])
        form = login_page_soup.select_one('form')
        data = {
            'email': self.USERNAME,
            'pass': self.PASSWORD
        }
        for input in form.select('input'):
            if 'name' in input.attrs and input['name'] not in ('email', 'pass'):
                data[input['name']] = input.get('value', None)
        response = self.post(
            form['action'],
            data=data
        )
        if not response.ok:
            raise ScraperAuthException('Failed to login.')
        if response.content.find('In order to confirm ownership of the page') \
                >= 0 or \
                        response.content.find('account from an unusual place') >= 0:
            self.log.info('Found confirmation check...')
            phone_soup = self.make_soup(response.content)
            form = phone_soup.select_one('form')
            response = self.post('https://m.vk.com' + form['action'],
                                 data={
                                     'code': '4095292',
                                     'submit': 'Confirm',
                                 }
                                 )
        # Should end up with a URL similar to:
        # http://api.vk.com/blank.html#access_token=9ac82b801aa3ac62b1b33e2475f7e09d5217e5252d0540a92fa01d7e230139e294c9a17c844ca2ffab2c6&expires_in=86400&user_id=258191591
        parsed_url = urlparse.urlparse(response.url)
        # Fragment is the bit after the hash; it's formatted like a qs.
        parsed_qs = urlparse.parse_qs(parsed_url.fragment)
        if 'access_token' not in parsed_qs:
            self.log.error('No token in %s -> %s', response.url, parsed_qs)
            raise ScraperAuthException('Could not find access token in url')

        return parsed_qs['access_token'][0]

    def _get_search_url(self, search_term, access_token, offset=0):
        search_url = self.BASE_URL + \
                     '/method/video.search?q=' + self.util.quote(search_term) + \
                     '&sort=1&filters=long&count=166' + \
                     '&offset=' + str(offset) + \
                     '&access_token=' + access_token
        return search_url

    def handle_video(self, video):
        image = video.get('image_medium', video.get('thumb', None))
        if 'link' in video:
            # in some cases (local videos?) we get links directly.
            url = 'http://vk.com/' + video['link'],
            self.submit_parse_result(
                parse_url=video['player'],
                link_url=url,
                link_title=video['title'],
                image=image,
            )
        elif 'player' in video:
            # Others we need to go parse.
            self.submit_search_result(
                link_url=video['player'],
                link_title=video['title'],
                image=image,
            )
        else:
            raise ScraperParseException('Could not find info from %s' % video)

    def search(self, search_term, media_type, **extra):
        self._do_search(search_term)

    def _do_search(self, search_term, retry=True):
        access_token = self._get_access_token()

        session = vk.Session(access_token=access_token)
        # Patch in our own session.
        session.requests_session = self.http_session()
        api = vk.API(session)

        offset = 0
        while True:

            # Try and fetch the videos...
            try:
                videos = api.video.search(
                    q=search_term,
                    offset=offset,
                    count=self.MAX_COUNT
                )
            except vk.exceptions.VkAPIError, e:
                self.log.exception('Exception on fetching videos.')
                # if our exception was due to too many calls, sleep and
                # try again.  Sleep a random time so we don't all wake
                # up at once.
                if 'Too many requests per second.' in str(e):
                    time.sleep(random.randint(10,120))
                else:
                    # Otherwise put it down to auth - reauth and try again.
                    self._clear_access_token()
                    session.access_token = self._get_access_token()

                # And try again.
                try:
                    videos = api.video.search(
                        q=search_term,
                        offset=offset,
                        count=self.MAX_COUNT
                    )
                except vk.exceptions.VkAPIError:
                    # If we fail, mark it.
                    raise ScraperAuthException(
                        'Could not fetch videos on second try: %s' % e)
            if not videos:
                if offset == 0:
                    self.submit_search_no_results()
                return
            for video in videos:
                self.handle_video(video)

            if len(videos) < self.MAX_COUNT or not self.can_fetch_next():
                break
            offset += len(videos)

    def parse(self, page_url, **extra):

        for page_soup in self.soup_each([page_url, ]):
            self._parse_parse_page(page_soup)

            index_page_title = page_soup.title.text.strip()

            foundany = False
            submitted = set()

            flashvars = page_soup.find('param', {'name': 'flashvars'})
            if flashvars:
                flashdata = urlparse.parse_qs(flashvars['value'])
                title = flashdata.get('md_title', [None, ])[0]
                for param in ('url240', 'url360', 'url480', 'url720'):
                    if param in flashdata:
                        foundany = True
                        link_url = flashdata[param][0]
                        if link_url not in submitted:
                            submitted.add(link_url)
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link_url,
                                link_title=title
                                )

            # Try and extract var vars.
            other_vars = []
            other_vars += re.findall('var vars = (\{.*\})', str(page_soup))
            other_vars += re.findall('var playerParams = (\{.*\})', str(page_soup))
            for varsset in other_vars:
                try:
                    vars = json.loads(varsset)
                except ValueError:
                    raise
                else:
                    params = vars['params']
                    for par in params:
                        title = par.get('md_title', None)
                        for param in ('url240', 'url360', 'url480', 'url720'):
                            if param in params[0]:
                                foundany = True
                                link_url = self.util.unquote(params[0][param])
                                if link_url not in submitted:
                                    submitted.add(link_url)
                                    self.submit_parse_result(
                                        index_page_title=index_page_title,
                                        link_url=link_url,
                                        link_title=title
                                    )

            for source in page_soup.select('source'):
                src = source.get('src')
                if src:
                    foundany = True
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=src,
                    )

            #parse results

            if not foundany:
                #self.log.warning(
                 #   'Could not find any video links from flash vars on: %s',
                 #   page_url)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=page_url,
                )

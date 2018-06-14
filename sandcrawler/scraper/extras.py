# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import shutil
import tempfile
import time
import base64
import urllib
import urlparse
import requests
from StringIO import StringIO

import selenium.webdriver.common.action_chains
from PIL import Image

from sandcrawler.scraper import deathbycaptcha
from sandcrawler.scraper.base import ScraperBase
from sandcrawler.scraper.exceptions import ScraperAuthException, \
    ScraperException, ScraperFetchException, ScraperFetchProxyException, \
    ScraperParseException


class SimpleScraperBase(ScraperBase):
    """
    A scraper that pre-populates a lot of functionality that is pretty
     generic.
     Any methods can be overridden, but these are required:
    BASE_URL
    _fetch_no_results_text(self)
    _parse_search_result_page(self, soup)
    _fetch_next_button(self, soup)
    _parse_parse_page(self, soup)


    NB: this could all move up to ScraperBase
    """

    BASE_URL = None

    def __init__(self, *args, **kwargs):
        if not self.BASE_URL:
            raise NotImplementedError('SimpleScraperBase requires BASE_URL')
        super(SimpleScraperBase, self).__init__(*args, **kwargs)

    def _fetch_no_results_text(self):
        raise NotImplementedError(
            'SimpleScraperBase requires _fetch_no_results_text')

    def _fetch_no_results_pattern(self):
        return None

    def _fetch_next_button(self, soup):
        raise NotImplementedError(
            'SimpleScraperBase requires _fetch_next_button')

    def _parse_search_result_page(self, soup):
        raise NotImplementedError(
            'SimpleScraperBase requires _parse_search_result_page')

    def _fetch_search_url(self, search_term, media_type):
        """
        Return a GET url for the search term; this is common, but you
         will often need to override this.
        """
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def search(self, search_term, media_type, **extra):
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        #  Using no_results_pattern

        no_results_pattern = self._fetch_no_results_pattern()
        if no_results_pattern and re.search(r'(?imsu)'+no_results_pattern,unicode(soup)):
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup)

    def _parse_iframes(self, soup, css_selector=None, **kwargs):
        if css_selector is None:
            css_selector = 'iframe'
        for iframe in soup.select(css_selector):
            src = iframe.get('src', iframe.get('data-src', None))
            if src:
                if 'index_page_title' not in kwargs:
                    kwargs['index_page_title'] = ''
                    try:
                        kwargs['index_page_title'] = soup.title.text.strip()
                    except:
                        pass

                self.submit_parse_result(link_url='http:' + src if src.startswith('//') else src,
                                         **kwargs
                                         )


class SimpleGoogleScraperBase(SimpleScraperBase):
    """
    More or less the same as simple scraper, but fills in details for a site
    that uses Google for its search.
    Some slight differences in what needs to be populated in a subclass.
    In most cases 'handle_search_result' may need to be overridden; default
    behaviour is to simply submit.
    Additionally normal parse operations are likely required.
    """

    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/43.0.2357.125 Safari/537.36'

    def _fetch_search_url(self, search_term, media_type):
        """
        Return a GET url for the search term; this is common, but you
         will often need to override this.

         Note that this uses Google.com - it will likely get redirected to
         the local Google, pending the proxy.
        """
        return 'https://www.google.com/search?q=' + \
               self.util.quote(search_term) + '&sitesearch=' + \
               self.util.get_domain(self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'did not match any documents'

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('a.pn')
        if next_link:
            return self.util.canonicalise('https://www.google.com', next_link.href)
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3.r a'):
            # Follow it so we get the URL.
            href = result['href']
            if href.startswith('/url'):
                try:
                    followed_response = self.get(
                        'https://www.google.com' + result['href'],
                        headers={
                            'User-Agent': self.USER_AGENT,
                        }
                    )
                    href = followed_response.url
                except ScraperException as error:
                    self.log.error("Scraper Error: %s", error)
                    continue
            self._handle_search_result(href, result.text)

    def _handle_search_result(self, url, link_title):
        self.submit_search_result(
            link_url=url,
            link_title=link_title,
        )


class EmbeddedGoogleScraperBase(ScraperBase):
    """
    Used for searches that embed google results within their own pages.
    For example, pastebin.

    Generally does a callback to
    https://www.googleapis.com/customsearch/v1element

    This should be returned by _fetch_search_url
    """

    def _fetch_search_url(self, search_term, media_type, start=None):
        """
        A Google GET URL based on the sites search.
        Note that start is basically paging - its an integer value to denote
        the first result returned.

         Must be implemented in child class as it's site specific.

         Note that many sites will include a callback=XXX parameter - remove
         that to just get JSON.
         Also note that the items per page (num=XX param) may be adjusted per
         site.
        """
        raise NotImplementedError('_fetch_search_url must be implemented in '
                                  'child class')

    def num_per_page(self):
        return 10

    def cleanup(self, json_text):
        json_text = json_text.replace('google.search.Search.apiary848(', '')\
            .replace(');', '').replace('// API callback', '')\
            .strip()
        return json_text


    def search(self, search_term, media_type, **extra):
        # Fetch our first page
        first_page = self.get(self._fetch_search_url(search_term, media_type)).text
        # Check we have any results
        jsoned_first_page = json.loads(self.cleanup(first_page))
        #jsoned_first_page = first_page.json()
        if not jsoned_first_page['results']:
            return self.submit_search_no_results()

        # Submit them.
        self._parse_search_result(jsoned_first_page)

        # work out if we have more pages to come
        result_count = int(jsoned_first_page['cursor']['estimatedResultCount'])
        per_page = self.num_per_page()
        pages = result_count / per_page
        page = 2
        while page < pages and self.can_fetch_next():
            try:
                new_page = self.get(
                    self._fetch_search_url(search_term, media_type,
                                           start=(page - 1) * per_page)
                )
            except ScraperFetchException, e:
                # There's no apparent indication of the 'last' page, so
                # if we fail with a bad request, it seems we've exhuasted
                # 'available' pages.
                # Allow that, but raise the exception otherwise.
                if e.data['status_code'] not in (400,):
                    raise
                break
            else:
                #self._parse_search_result(search_json=new_page.json())
                self._parse_search_result(search_json=json.loads(self.cleanup(new_page.text)))
                page += 1

    def _parse_search_result(self, search_json):
        found = False
        for result in search_json['results']:
            self.submit_search_result(
                link_url=result['url'],
                link_title=result['titleNoFormatting']
            )
            found = True
        if not found:
            self.submit_search_no_results()


class DuckDuckGo(SimpleScraperBase):
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/43.0.2357.125 Safari/537.36'

    def search(self, search_term, media_type, **extra):
        search_url = 'https://duckduckgo.com/?q={}+site%3A{}&t=h_&ia=web'.format(
             self.util.quote(search_term), self.util.get_domain(self.BASE_URL))
        # print search_url
        page = self.get(search_url)
        # print page.text
        self._parse_search_result_page(page.text)


    def _fetch_next_button(self, soup):
        text_page = unicode(soup)
        if '!DOCTYPE html' in text_page:
            json_soup = soup.find_all('script')[-3].text.split(";nrje('")[-1].split("','")[0]
        else:
            json_soup = json.loads(text_page.split("resultLanguages\',")[-1].split("nrn(\'d\',")[-1].split(');')[0])[-1]['n']
        return 'https://duckduckgo.com' + json_soup

    def _fetch_no_results_text(self):
        return 'No more results.'

    def _parse_search_result_page(self, soup):
        text_page = soup
        if type(text_page) is unicode:
            if '!DOCTYPE html' in text_page:
                json_soup = self.make_soup(text_page).find_all('script')[-3].text.split(";nrje('")[-1].split("','")[0]
                if 'wt-wt' in json_soup:
                    json_soup = json_soup.replace('wt-wt', 'ru-ru').replace('us-en', 'ru-ru').replace('&ss_mkt=us', '')
                first_button = 'https://duckduckgo.com' + json_soup
                if self.can_fetch_next() and first_button:
                    self._parse_search_result_page(
                        self.get(first_button)
                    )
        else:
            js_text = text_page.text.split("resultLanguages\',")[-1].split("nrn(\'d\',")[-1].split(');')[0].strip('[').strip(']')
            js_text_list = js_text.split('},{')
            for js_txt_list in js_text_list:
                if '{' in js_txt_list[0] and '}' in js_txt_list[-1]:
                    text_dictionary = js_txt_list
                if '{' not in js_txt_list[0] and '}' not in js_txt_list[-1]:
                    text_dictionary = '{' + js_txt_list + '}'
                if '{' in js_txt_list[0] and '}' not in js_txt_list[-1]:
                    text_dictionary = js_txt_list + '}'
                if '{' not in js_txt_list[0] and '}' in js_txt_list[-1]:
                    text_dictionary = '{' + js_txt_list
                try:
                    row = json.loads(text_dictionary)
                except ValueError:
                    continue
                url = link_title = ''
                try:
                    eof = row['d']
                    if eof == 'google.com search' and len(js_text_list)==1:
                        return self.submit_search_no_results()
                    if row['a']:
                        url = row['c']
                        link_title = row['t']
                except KeyError:
                    pass
                next_page = ''
                try:
                    next_page = row['n'].replace('us-en', 'ru-ru')
                except KeyError:
                    pass
                if next_page and self.can_fetch_next():
                    self._parse_search_result_page(
                        self.get_soup('https://duckduckgo.com'+next_page)
                    )
                if not url:
                    continue
                if 'https://www.google.com/search' not in url:
                    self.submit_search_result(
                        link_url=url,
                        link_title=link_title,
                    )


class OpenSearchMixin(object):
    """
    A seemingly common application with 'standard' search and pagination.
     Provides a few methods for accessing things easily.
     A few examples:
     www.full-streaming.com
     www.downturk.biz

     look for 'story' as a POSTed search param.

     Needs to mixed in with a SimpleScraperBase, and have the following defined:

      BASE_URL
      _parse_search_results(soup)

     Optional settings for Advanced search:
        self.bunch_size = 20                          - how many search results return per page   (default 10)
        self.media_type_to_category = 'film 4, tv 5'  - search categories (catlist[] aka subforums) No's mapping
        self.encode_search_term_to = 'utf256'         - encoding to convert search_term before submitting
        self.showposts = 1 or 0                       - show results as:   articles /  titles     (default 1)
    """
    # Overridable settings for sanity tests.
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def search(self, search_term, media_type, **extra):
        self.media_type = media_type
        first_page = self.load_search_page(search_term)
        self._parse_search_results(first_page)
        # Then suck out our other pages - looks like it's capped at 5
        for page in first_page.findAll(
                'a',
                onclick=re.compile('^javascript:list_submit\(\d+\)')):
            if not self.can_fetch_next():
                break
            try:
                page_no = int(page.text)
            except ValueError:
                pass
            else:
                self.log.debug('---------- {} ----------'.format(page_no))
                self._parse_search_results(
                    self.load_search_page(search_term, page_no)
                )

    def _fetch_no_results_text(self):
        return dict(
            rus=u'К сожалению, поиск по сайту не дал никаких результатов',
            fra=u'La recherche n\'a retourné aucun résultat.'
        ).get(self.search_term_language,
              'The search did not return any results.')

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and \
                        unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)

    def _search_with_get(self):
        """
        Return True to  use a GET for the search page.
        """
        return False

    def _request_headers(self):
        return {}

    def _fetch_search_url(self, search_term):
        return self.BASE_URL + '/index.php?do=search'

    def _include_xy_in_search(self):
        return True

    def _fetch_search_params(self, search_term, page):
        search_params = {
            'do': 'search',
            'subaction': 'search',
            # 'full_search' : 0,
            'story': search_term.decode(self.search_term_encoding).encode(
                self.encode_search_term_to, errors='ignore')
            if 'encode_search_term_to' in self.__dict__
            else search_term
        }
        if self._include_xy_in_search():
            search_params.update({
                'x': 0,
                'y': 0,
            })
        if page:
            search_params['search_start'] = int(page)
            search_params['result_from'] = (
                    int(page) * getattr(self, 'bunch_size',10)
                ) - (
                    getattr(self, 'bunch_size', 10) - 1
                )

        if 'showposts' in self.__dict__ or 'media_type_to_category' in self.__dict__:
            # Advanced search settings are set
            search_params.update(
                full_search=1,
                titleonly=3,
                searchuser='',
                replyless='0',
                replylimit='0',
                searchdate='0',
                beforeafter='after',
                sortby='',
                showposts=getattr(self, 'showposts', 1),
                result_num=getattr(self, 'bunch_size', 10),
                resorder='desc')

            try:
                search_params['catlist[]'] = (
                    dict([cat2num.strip().split(' ') for cat2num in
                          self.media_type_to_category.split(',')]).get(
                        self.media_type, 0)
                    if 'media_type_to_category' in self.__dict__
                    else 0)
            except Exception as e:
                raise e.__class__(
                    'Please specify media_type to site category mapping in the format like "film 3, tv 10"')

            if 'x' in search_params:
                del search_params['x']
            if 'y' in search_params:
                del search_params['y']

        return search_params

    def load_search_page(self, search_term, page=None):
        search_url = self._fetch_search_url(search_term)
        search_params = self._fetch_search_params(search_term, page)




        if self._search_with_get():
            if urlparse.urlparse(search_url).query:
                search_url += '&' + urllib.urlencode(search_params)
            else:
                search_url += '?' + urllib.urlencode(search_params)
            return self.get_soup(
                search_url,
                headers=self._request_headers())
        else:
            search_params['do'] = 'search'
            return self.post_soup(
                search_url,
                data=search_params,
                headers=self._request_headers())


class VKAPIMixin(object):
    """
    Mixin to provide a method of fetching info from the api.vk.com website
    which is used in a few places.
    """

    def _fetch_from_vk_api(self, oid, v_id, hash):
        vk_url = 'https://api.vk.com/method/video.getEmbed' \
                 '?oid=' + oid + \
                 '&video_id=' + v_id + \
                 '&embed_hash=' + hash
        vk_resp = self.get(vk_url)
        json_info = json.loads(vk_resp.text)
        # Or check for 'error'
        if 'response' in json_info:
            for k, v in json_info['response'].items():
                if k.startswith('url'):
                    yield v


class VBulletinMixin(object):
    """
    Mixin that handles VBulletin logins with md5 handling.
    """

    # Some sites will allow 'guest' as your security token; others require
    # you to submit a legitimate value.
    ALLOW_GUEST_TOKEN = True
    SECURITY_TOKEN_NAME = 'security_token'

    def __check_attrs(self):
        """
        Make sure we have all the info we need.
        """
        for field in ('BASE_URL', 'USERNAME', 'PASSWORD'):
            if not hasattr(self, field) or not getattr(self, field):
                raise NotImplementedError('%s required for VBulletin', field)

    def _get_login_url(self):
        return self.BASE_URL + '/login.php?do=login'

    def _login_success_string(self):
        return 'Thank you for logging in'

    def _is_valid_login(self, content):
        # This may need to be over ridden on foreign language sites.
        if content.find(self._login_success_string()) == -1:
            raise ScraperAuthException('Failed to login to VBulletin')
        return True

    def _get_security_token(self):
        if self.ALLOW_GUEST_TOKEN:
            return 'guest'
        else:
            home_soup = self.get_soup(self.BASE_URL)
            # TODO catch not found and raise parse error.
            token_input = home_soup.find('input',
                                         {'name': self.SECURITY_TOKEN_NAME})
            return token_input['value']

    def _md5password(self):
        return hashlib.md5(self.PASSWORD).hexdigest()

    def _login_post_data(self):
        md5_password = self._md5password()
        login_data = {
            'vb_login_username': self.USERNAME,
            'vb_login_password': '',
            'vb_login_password_hint': '',
            'securitytoken': self._get_security_token(),
            'do': 'login',
            'vb_login_md5password': md5_password,
            'vb_login_md5password_utf': md5_password,
        }
        return login_data

    def _login(self):
        """
        Handles a login - should be called before doing login-required events
        like search or parse.
        """
        # Do a couple of preflight checks
        self.__check_attrs()

        response = self.post(
            self._get_login_url(),
            data=self._login_post_data(),
        )
        return self._is_valid_login(response.content)

    def _find_next_link(self, soup):
        link = soup.find('a', {'rel': 'next'})
        return self.BASE_URL + '/' + link['href'] if link else None


class FlashVarsMixin(object):
    """
    Mixin that allows parsing out of flashvar values, which seem to be
    a pretty common api setup.
    """

    def _parse_flashvars_from_query_string(self, qstring):
        self._parse_flashvars(
            urlparse.parse_qs(qstring)
        )

    def _parse_flashvars_from_javascript_hash(self, javascriptstring):
        params = {}
        for fieldname in ('pl', 'file', 'poster'):
            match = re.search("'?%s'?:'(.*?)'" % fieldname,
                              javascriptstring)
            if match:
                params[fieldname] = match.group(1)
        self._parse_flashvars(params)

    def _parse_flashvars_from_json_string(self, jsonstring):
        self._parse_flashvars(
            json.loads(jsonstring)
        )

    def _parse_flashvars(self, params):
        """
        Accepts a dict and submits search results from it.
        The params are generally built from either a json reference
         in javascript, or a query string style entry in a
         <param name="flashvars" value="....">
        """
        if 'file' in params:
            self._extract_file(params)
        if 'pl' in params:
            self._extract_playlist(params)

    def _extract_file(self, params):
        """
        Suck a single file out of a params dict.
        """
        file_list = params['file']
        if type(file_list) is not list:
            file_list = [file_list, ]
        for file in file_list:
            link_title = None
            if 'comment' in params:
                link_title = params['comment']
                if type(link_title) is list:
                    link_title = link_title[0]
            image = None
            if 'poster' in params:
                image = params['poster']
                if type(image) is list:
                    image = image[0]
                if not image.startswith('http'):
                    image = self.BASE_URL + image
            self.submit_parse_result(
                index_page_title=self.soup2parse.title.text.strip() if 'soup2parse' in self.__dict__ else '',
                link_url=file,
                link_title=link_title,
                image=image,
                asset_type=ScraperBase.MEDIA_TYPE_FILM,
            )

    def _extract_playlist(self, params):
        """
         Potentially nested playlists
         - first level is season, second is episode.
         - OR, first level is just episode for a single season.
        """
        playlist_url = params['pl']
        if type(playlist_url) is list:
            playlist_url = playlist_url[0]
        if not playlist_url.startswith('http'):
            playlist_url = self.BASE_URL + playlist_url

        decoded_response = self.get(playlist_url) \
            .content \
            .decode('utf-8-sig')
        playlist = json.loads(decoded_response)
        for pl in playlist['playlist']:
            # Nested
            if 'playlist' in pl:
                season = self.util.find_numeric(
                    pl.get('comment', ''))
                for episode_pl in pl['playlist']:
                    episode = self.util.find_numeric(
                        episode_pl.get('comment', ''))
                    self.submit_parse_result(
                        index_page_title=self.soup2parse.title.text.strip() if 'soup2parse' in self.__dict__ else '',
                        link_url=episode_pl['file'],
                        series_season=season,
                        series_episode=episode,
                        asset_type=ScraperBase.MEDIA_TYPE_TV,
                    )
            elif 'file' in pl:
                season = 1
                episode = self.util.find_numeric(
                    pl.get('comment', ''))
                self.submit_parse_result(
                    index_page_title=self.soup2parse.title.text.strip() if 'soup2parse' in self.__dict__ else '',
                    link_url=pl['file'],
                    series_season=season,
                    series_episode=episode,
                    asset_type=ScraperBase.MEDIA_TYPE_TV,
                )


class PHPBBMixin(object):
    """
    Provides useful PHPBB methods, namely:
    - _login  - requires self.USERNAME and self.PASSWORD
    - _do_search - requres self.FORUMS
    - _fetch_next_button - for use in the simple scraper setup.

    All require self.BASE_URL
    """
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/43.0.2357.125 Safari/537.36'

    def _login_success_text(self):
        return 'You have successfully logged in'

    def _login(self):
        self.get(self.BASE_URL + '/login.php')
        response = self.post(
            self.BASE_URL + '/login.php',
            data={
                'username': self.USERNAME,
                'password': self.PASSWORD,
                'autologin': 'on',
                'redirect': '',
                'login': 'Log in',
            },
            headers={'Origin': self.BASE_URL,
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Referer': self.BASE_URL + 'login.php',

                     }
        )
        if not response.content.find(self._login_success_text()) >= 0 and not 'Log out' in response.content:
            raise ScraperAuthException('Could not login')

    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL + '/search.php?mode=results',
            data={
                'search_keywords': search_term,
                'search_terms': 'all',
                'search_author': '',
                'search_forum%5B%5D': self.FORUMS,
                'search_time': 0,
                'search_fields': 'titleonly',
                'sort_by': 0,
                'sort_dir': 'DESC',
                'show_results': 'topics',
                'return_chars': 200
            },
            headers={'Origin': self.BASE_URL,
                     'Accept-Encoding': 'gzip, deflate',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Referer': self.BASE_URL + '/search.php',
                     'User-Agent': self.USER_AGENT,
                     })


class PHPBBSimpleScraperBase(PHPBBMixin, SimpleScraperBase):
    """
    A class that provides simplesearch and phpbb utilities - subclass should
    just need to provide:
    BASE_URL
    USERNAME
    PASSWORD
    FORUMS

    Perhaps, depending on styling and languages, some parsing functionatlity and
    text return functions like _fetch_no_results_text
    """

    def _fetch_no_results_text(self):
        return 'No topics or posts met your search criteria.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        if link:
            return self.BASE_URL + '/' + link['href']
        return None

    def search(self, search_term, media_type, **extra):
        self._login()
        self.get(self.BASE_URL + '/search.php')
        self._parse_search_results(self._do_search(search_term))

    def parse(self, page_url, **kwargs):
        self._login()
        super(PHPBBSimpleScraperBase, self).parse(page_url, **kwargs)

    def _parse_search_result_page(self, soup):
        for link in soup.select(
                'div.list-wrap div.list-rows div.topicrow span.topictitle a'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        # This is generic, but find any div.codes, then regex out and link looking things.
        for codeblock in soup.select('div.code'):
            for link in self.util.find_urls_in_text(str(codeblock)):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link
                                         )

class CachedCookieSessionsMixin(object):
    """
    Gives the ability to cache session cookies.
    Useful for sites with a heavy verification method (eg a login, or a captcha)

    General flow:
    - call load_session_cookies
    - perform a check to see if the task is needed (eg is there a captcha on
    page, or a login prompt?)
    - if needed, do the action.
    - if action performed, call save_session_cookies.
    """

    def _cache_key_name(self):
        return '{}_cookies'.format(self.__class__.__name__)


    def _load_cookies(self):
        from sandcrawler.scraper.caching import cache
        import redis_cache
        try:
            cookies = cache.get_pickle(self._cache_key_name())
        except (redis_cache.ExpiredKeyException,
                redis_cache.CacheMissException):
            self.log.debug('Failed loading cookies from cache.')
            return None
        else:
            if not cookies:
                self.log.debug('Loaded blank cookies from cache - discarding')
                return None
            self.log.debug('Successfully loaded cookies from cache.')
            return cookies

    def load_session_cookies(self):
        """
        Load session cookies into our http session.
        """
        # Make sure we have an initt'd http session.
        self.http_session()
        cookies = self._load_cookies()
        if cookies:
            for name, value, domain in cookies:
                self._http_session.cookies.set(name, value, domain=domain)

    def save_session_cookies(self):
        """
        Store these validated cookies into the cache for use later.
        :return:
        """

        cookies = []
        for cookie in self._http_session.cookies:
            cookies.append(
                (cookie.name, cookie.value, cookie.domain)
            )
        from sandcrawler.scraper.caching import cache
        self.log.debug('Saving %s cookies', len(cookies))
        cache.store_pickle(
            self._cache_key_name(),
            cookies
        )


class WebdriverSessionExtractionMixin(object):
    """
    A utility mixin to allow for getting parameters from a webdriver, and using
    them in a (simpler) http requests session.
    """

    BASE_CACHEKY = 'WDSESSION'
    COOKIES_CACHEKEY = 'cookies'
    USERAGENT_CACHEKEY = 'useragent'

    COOKIE_NAMES = None

    def _get_cache_key(self, part):
        return '%s_%s_%s' % (
            self.BASE_CACHEKY, part, self.__class__.__name__)

    def _cache_retrieve(self, key):
        from sandcrawler.scraper.caching import cache
        import redis_cache
        try:
            cookies = cache.get_pickle(key)
        except (redis_cache.ExpiredKeyException,
                redis_cache.CacheMissException):
            self.log.info('Failed loading cookies from cache.')
            return None
        else:
            if not cookies:
                self.log.warning('Loaded blank cookies from cache - discarding')
                return None
            self.log.info('Successfully loaded cookies from cache.')
            return cookies

    def _cache_store(self, key, value):
        from sandcrawler.scraper.caching import cache
        cache.store_pickle(key, value)

    def _cache_clear(self):
        from sandcrawler.scraper.caching import cache
        cache.invalidate(self._get_cache_key(self.COOKIES_CACHEKEY))
        cache.invalidate(self._get_cache_key(self.USERAGENT_CACHEKEY))

    def _get_cookies(self, tries=0):
        cookies = self._cache_retrieve(self._get_cache_key(self.COOKIES_CACHEKEY))
        if cookies:
            return cookies

        lock = None
        # if we have a locking attribute
        if hasattr(self, 'locking') and self.locking:
            self.log.info('Attempting to lock session action')

            lock = self.locking.acquire_lock(
                'sessionaction',
                [self.__class__.__name__, ],
                expiry=60, # 1 second.
            )
            if not lock:
                # if we've been trying to omuch, bail out.
                if tries > 10:
                    self.log.error('Could not acquire lock for session action after %s tries.  Failing.', tries)
                    raise ValueError('Could not acquire lock for session action after %s tries.  Failing.' % tries)
                # if we couldn't get the lock, delay for a bit then try again.
                # depending on the try cutoff this will add up (0, 2, 4, 6, etc up to 20 seconds on the 10th try)
                sleep_for = tries * 2
                self.log.warning('Could not get lock.  Sleeping %s', sleep_for)
                time.sleep(sleep_for)
                return self._get_cookies(tries = tries + 1)

        self.log.info('Loading cookies from webdriver and caching.')

        try:
            wd = self.webdriver()
            self.perform_action()
            cookie_values = []
            for cookie in wd.get_cookies():
                if cookie['name'] in self.COOKIE_NAMES:
                    cookie_values.append(
                        (cookie['name'], cookie['value'], cookie['domain'])
                    )

            self._cache_store(self._get_cache_key(self.COOKIES_CACHEKEY),
                              cookie_values)
        finally:
            if lock:
                lock.release()

        return cookie_values

    def perform_action(self):
        raise NotImplementedError(
            'You must specify an action for the webdriver to retrieve cookies'
        )

    def _get_http_user_agent(self):
        user_agent = self._cache_retrieve(
            self._get_cache_key(self.USERAGENT_CACHEKEY))
        if user_agent:
            return user_agent

        driver = self.webdriver()
        try:
            # This works for phantom
            user_agent = driver.capabilities['phantomjs.page.settings.userAgent']
        except KeyError:
            # This works for chrome
            user_agent = self.webdriver().execute_script("return navigator.userAgent")

        self._cache_store(
            self._get_cache_key(self.USERAGENT_CACHEKEY), user_agent)
        return user_agent

    def http_session(self):
        # Builds a http session, but with cookies already
        self.log.info('Building http_session with cookies.')
        http_session = super(
            WebdriverSessionExtractionMixin,
            self).http_session()
        for name, value, domain in self._get_cookies():
            http_session.cookies.set(name, value, domain=domain)

        return http_session


class WebDriverScreenshotMixin(object):
    """
    A mixin that expects to have the webdriver available, and will grab a
    screenshot of an element on screen.
    """

    THUMBSIZE = (400, 400)

    def get_element_screenshot(
            self,
            element,
            extra_xoffset=0,
            extra_yoffset=0,
    ):
        return self.get_element_screenshot_with_size(
            element,
            extra_xoffset=extra_xoffset,
            extra_yoffset=extra_yoffset,
        )[0]

    def get_element_screenshot_with_size(
            self,
            element,
            extra_xoffset=0,
            extra_yoffset=0,
    ):
        wd = self.webdriver()
        self.log.debug('Screenshotting full screen.')
        outdata = wd.get_screenshot_as_png()
        img = Image.open(StringIO(outdata))

        location = element.location
        left = int(location['x']) + extra_xoffset
        top = int(location['y']) + extra_yoffset
        size = element.size
        right = int(left + size['width'])
        bottom = int(top + size['height'])

        self.log.debug('Cropping screenshot at %s, %s, %s, %s',
                       left, top, right, bottom)
        cropped = img.crop(
            [left, top, right, bottom]
        )

        cropped_tmp = tempfile.NamedTemporaryFile(
            suffix='.png',
            delete=False,
            prefix='sandcrawler_wdss',
        )
        cropped_tmp.close()

        self.log.debug('Saving screenshot to %s', cropped_tmp.name)
        if self.THUMBSIZE:
            cropped.thumbnail(self.THUMBSIZE)
        cropped.save(cropped_tmp.name)

        return cropped_tmp.name, cropped.size


class DeathByCaptchaMixin(object):
    """
    Implementation of a DeathByCaptcha solver.

    Basically a mixin that provides two (usefl) function calls:
    - solve_captcha
      This accepts either a url, or a local path to an image.
      It does the actual callout to the DeathByCaptcha service, and either
      returns a string of the expected result or raises an error.

    - mark_bad_captcha
      This should be called when the captcha result was incorrect.  It is vital
      to call it, as the captcha will be paid for even if it was not correct.

    """

    DEATHBYCAPTCHA_USERNAME = "xoo7phai"
    DEATHBYCAPTCHA_PASSWORD = "3jjfxjeQnwJqqK0l"
    DEATHBYCAPTCHA_TIMEOUT = 25  # average seems to be 9... this should be heaps?

    @property
    def client(self):
        if not hasattr(self, '_client'):
            # raises?
            self._client = deathbycaptcha.SocketClient(
                self.DEATHBYCAPTCHA_USERNAME,
                self.DEATHBYCAPTCHA_PASSWORD
            )
        return self._client

    def _get_temp_file(self, format='.png'):
        tmpfile = tempfile.NamedTemporaryFile(
            suffix=format,
            delete=False,
            prefix='sandcrawler_dbc',
        )
        return tmpfile

    def download_image(self, url, format='.png'):
        # TODO - md5 and cach this?
        response = self.http_session().get(url, stream=True)
        tmpfile = self._get_temp_file(format)
        filename = tmpfile.name
        self.log.debug('Downloading captcha to %s', filename)
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, tmpfile)
        self.log.debug('Downloaded to %s', filename)
        return filename

    def remove_image(self, filename):
        if os.path.exists(filename):
            self.log.debug('Removing %s', filename)
            # os.remove(filename)

    def solve_captcha(self, url=None, image_filename=None, format='.png'):
        return self._solve_captcha(
            url=url, image_filename=image_filename, format=format
        )['text']

    def _solve_captcha(
            self,
            url=None,
            image_filename=None,
            format='.png',
            decode_kwargs=None
    ):
        if not url and not image_filename:
            raise NotImplementedError(
                'solve_captcha requires either an image url or image_filename')
        try:
            if not image_filename:
                image_filename = self.download_image(url, format=format)

            self.captcha = None
            self.log.debug('Trying captcha for %s / %s', url, image_filename)
            try:
                balance = self.client.get_balance()
                if balance <= 2:
                    raise ScraperAuthException(
                        'Low balance on DEATHBYCAPTCHA: %s' % balance
                    )
                if decode_kwargs is None:
                    decode_kwargs = {}
                self.captcha = self.client.decode(
                    image_filename,
                    self.DEATHBYCAPTCHA_TIMEOUT,
                    **decode_kwargs
                )
                if self.captcha:
                    self.log.info(
                        'Received captcha result: %s', self.captcha
                    )
                    return self.captcha
                else:
                    self.log.error(
                        'No result for captcha: %s', url
                    )
                    raise ScraperAuthException(
                        'DEATHBYCAPTCHA did not return a result.'
                    )

            except deathbycaptcha.AccessDeniedException:
                self.log.exception(
                    'Error connecting to deathbycapcha'
                )
                raise ScraperAuthException(
                    'Error connecting to DEATHBYCAPTCHA'
                )
        finally:
            if image_filename:
                self.remove_image(image_filename)

    def mark_bad_captcha(self):
        self.client.report(
            self.captcha['captcha']
        )


class DeathByCaptchaOldReCaptchaMixin(
    DeathByCaptchaMixin,
    WebDriverScreenshotMixin):
    """
    An extension of DeathByCaptcha allowing use of the webdriver to screenshot
    and solve captchas.

    Specifically in use for recaptchas like:
    http://softsclub.com/search.php?do=process

    But could be used for others.

    Again, it is vital to call mark_bad_captcha on a failed result.
    """

    def fill_recaptcha_input(self, ):
        wd = self.webdriver()
        # Find the image element, screenshot it and send to DBC
        image_element = wd.find_element_by_id('recaptcha_challenge_image')
        image_screenshot = captcha_result = None
        try:
            self.log.debug('Screenshotting element.')
            image_screenshot = self.get_element_screenshot(image_element)
            self.log.debug('Solving captcha')
            captcha_result = self.solve_captcha(
                image_filename=image_screenshot
            )
        finally:
            if image_screenshot:
                self.remove_image(image_screenshot)

        if captcha_result:
            # find the response field and fill in our result.
            response_field = wd.find_element_by_id('recaptcha_response_field')
            response_field.send_keys(captcha_result)
        else:
            raise ScraperParseException('No captcha result found.')


class DeathByCaptchaReCaptchaMixin(
    DeathByCaptchaMixin,
    WebDriverScreenshotMixin,
    WebdriverSessionExtractionMixin
):
    DEATHBYCAPTCHA_TIMEOUT = 60  # average seems to be 9... this should be heaps?

    COOKIE_NAMES = ('rc',)
    BASE_CACHEKY = 'DBCRECAPTCHA'

    def find_iframe(self, name='recaptcha widget'):
        for iframe in self.webdriver().find_elements_by_tag_name('iframe'):
            if iframe.get_attribute('title') == name:
                return iframe
        return None

    def _click_tick(self):
        wd = self.webdriver()
        iframe = self.find_iframe()
        if not iframe:
            raise ScraperParseException('Could not find recaptcha widget iframe')

        wd.switch_to.frame(iframe)
        tick_element = wd.find_element_by_css_selector(
            'div.recaptcha-checkbox-checkmark')
        tick_element.click()
        wd.switch_to.window(
            wd.window_handles[0]
        )

    def _click_chain(self, element, click_locations):
        chain = selenium.webdriver.common.action_chains.ActionChains(
            self.webdriver())
        for location_x, location_y in click_locations:
            chain.move_to_element_with_offset(
                element,
                location_x,
                location_y)
            chain.click()
        chain.perform()

    def _get_captcha_element(self):
        return self.webdriver().find_element_by_xpath(
            '//*[@id="rc-imageselect"]'
        )

    def _extract_advanced_captcha(self):
        wd = self.webdriver()
        iframe = self.find_iframe(name='recaptcha challenge')
        iframe_location = iframe.location

        wd.switch_to.frame(iframe)

        captcha_element = self._get_captcha_element()
        captcha, size = self.get_element_screenshot_with_size(
            captcha_element,
            extra_xoffset=int(iframe_location['x']),
            extra_yoffset=int(iframe_location['y']),
        )

        # Because we thumbnail the images, we need to re-adjust the reulsting
        # click locations so they're in the right spot on page.
        size_on_screen = captcha_element.size
        x_multiplier = float(size_on_screen['width']) / float(size[0])
        y_multiplier = float(size_on_screen['height']) / float(size[1])

        captcha_result = self._solve_captcha(
            image_filename=captcha,
            decode_kwargs={'type': 2}
        )

        click_locations = json.loads(captcha_result['text'])
        adjusted_click_locations = [
            (x * x_multiplier, y * y_multiplier) for (x, y) in click_locations
            ]

        # add 100 to each vertical...
        self._click_chain(captcha_element, adjusted_click_locations)

        # And verify
        wd.find_element_by_xpath(
            '//*[@id="recaptcha-verify-button"]'
        ).click()

        time.sleep(10)

        # Switch back to the main screen.
        wd.switch_to.window(wd.window_handles[0])
        # and see if the iframe for recapcha is still there.
        if self.find_iframe():
            self.mark_bad_captcha()
            raise ScraperParseException('Could not pass ReCaptcha')

        # Otherwise, we're good :D
        return True

    def solve_recaptcha(self):
        self._click_tick()
        time.sleep(3)
        self._extract_advanced_captcha()

    def perform_action(self):
        self.webdriver().get(self.BASE_URL)


class AntiCaptchaImageMixin(object):

    CLIENT_KEY = "8104b4407a78dc93129979fa13338a35"

    def _get_temp_file(self, format='.png'):
        tmpfile = tempfile.NamedTemporaryFile(
            suffix=format,
            delete=False,
            prefix='sandcrawler_anticap_',
        )
        return tmpfile

    def download_image(self, url, format='.png'):
        response = self.http_session().get(url, stream=True)
        tmpfile = self._get_temp_file(format)
        filename = tmpfile.name
        self.log.debug('Downloading captcha to %s', filename)
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, tmpfile)
        self.log.debug('Downloaded to %s', filename)
        return filename


    def solve_captcha(self, image_url, phrase=False, case=False, numeric=0, math=False, minLength=0, maxLength=0, format='.png'):
        image_file = self.download_image(image_url, format=format)
        with open(image_file, "rb") as f:
            body = base64.b64encode(f.read())
            request_body = json.dumps(
                {
                    "clientKey": self.CLIENT_KEY,
                    "task": {
                        "type": "ImageToTextTask",
                        "body":body,
                        "phrase":phrase,
                        "case":case,
                        "numeric":numeric,
                        "math":math,
                        "minLength":minLength,
                        "maxLength":maxLength
                    }
                })
            response = requests.post(
                'http://api.anti-captcha.com/createTask',
                data=request_body,
            )
            if not response.ok:
                raise ValueError('Received response from anticaptcha: {}'.format(
                    response.text,
                ))
            task_id = response.json().get('taskId')
            if not task_id:
                raise ValueError(
                    'Could not find task id in anticaptcha response: {}'.format(
                        response.text
                    ))
            if task_id:
                body = json.dumps({
                    "clientKey": self.CLIENT_KEY,
                    "taskId": task_id,
                })
                resp = requests.post(
                    'http://api.anti-captcha.com/getTaskResult',
                    data=body,
                )
                response = resp.json()
                while response['status'] == 'processing':
                    time.sleep(5)
                    resp = requests.post(
                        'http://api.anti-captcha.com/getTaskResult',
                        data=body,
                    )
                    response = resp.json()
                    if response['status'] == 'ready':
                        text = response['solution']['text']
                        break
                else:
                    raise ValueError(
                            'No text in anticaptcha response: {}'.format(
                                response
                            ))
                return text


class AntiCaptchaMixin(object):

    CLIENT_KEY = "8104b4407a78dc93129979fa13338a35"

    def get_recaptcha_token(self):
        if not getattr(self, 'RECAPKEY'):
            raise ValueError(
                'AntiCaptchaMixin requires a RECAPKEY')
        recap_url = getattr(self, 'RECAPURL', self.BASE_URL)
        self.log.info('Starting recap solve for {}'.format(recap_url))
        request_body = json.dumps(
            {
                "clientKey": self.CLIENT_KEY,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": recap_url,
                    "websiteKey": self.RECAPKEY,
                }
            }
        )
        response = requests.post(
            'http://api.anti-captcha.com/createTask',
            data=request_body,
        )
        if not response.ok:
            raise ValueError('Received response from anticaptcha: {}'.format(
                response.text,
            ))
        task_id = response.json().get('taskId')
        if not task_id:
            raise ValueError(
                'Could not find task id in anticaptcha response: {}'.format(
                    response.text
                ))
        tries = 0
        key = None
        while tries < 20:
            time.sleep(5)
            tries += 1
            self.log.info('Checking result for taskid={} tries={}'.format(
                task_id, tries
            ))
            body = json.dumps({
                 "clientKey": self.CLIENT_KEY,
                 "taskId": task_id,
            })
            resp = requests.post(
                'http://api.anti-captcha.com/getTaskResult',
                data=body,
            )

            if not resp.ok:
                continue
            response = resp.json()
            if response['status'] == 'ready':
                key = response['solution']['gRecaptchaResponse']
                self.log.warning('Recaptcha solve for domain {}'.format(recap_url))
                break

        if not key:
            raise ValueError('Key not found for taskid {} after {} tries',
                task_id, tries)

        return key


class CloudFlareDDOSProtectionMixin(AntiCaptchaMixin, WebdriverSessionExtractionMixin):
    BASE_CACHEKY = 'CLOUDFLARE_DDOS'
    COOKIE_NAMES = (
        '__cfduid',
        'cf_clearance',
        'rc'
    )
    RECAPKEY = '6LfBixYUAAAAABhdHynFUIMA_sa4s-XsJvnjtgB0'

    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def get(self, *args, **kwargs):
        headers = kwargs.get('headers',
                             {'user-agent': self._get_http_user_agent()})
        kwargs['raise_proxy_errors'] = True
        kwargs['headers'] = headers
        try:
            return super(CloudFlareDDOSProtectionMixin, self).get(*args, **kwargs)
        except ScraperFetchProxyException:
            # Cloudflare sends a 503 - clear our values, get new ones
            # and try again.
            self.log.info('Received proxy exception for CF request - clearing '
                'cache and trying again.')
            self._cache_clear()
            return super(CloudFlareDDOSProtectionMixin, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        headers = kwargs.get('headers', {})
        if 'user-agent' not in headers:
            headers['user-agent'] = self._get_http_user_agent()

        kwargs['headers'] = headers
        return super(CloudFlareDDOSProtectionMixin, self).post(*args, **kwargs)

    def cloudflare_wait(self):
        return 6

    def cloudflare_tries(self):
        return 4

    def _get_cloudflare_action_url(self):
        return self.BASE_URL

    def perform_action(self):
        action_url = self._get_cloudflare_action_url()
        self.log.info('Fetching %s for Cloudflare cookies.', action_url)
        wd = self.webdriver()
        wd.set_page_load_timeout(200)
        wd.get(action_url)
        tries = 0
        if 'recaptcha' in wd.page_source and 'challenge-form' in wd.page_source:
            self.log.info('Found recaptcha on page; attempting to solve.')
            download_id = self.make_soup(wd.page_source).select_one('form#challenge-form').find_next('script')['data-ray']
            key = self.get_recaptcha_token()
            if key:
                wd.get('{}/cdn-cgi/l/chk_captcha?id={}&g-recaptcha-response={}'.format(self.BASE_URL, download_id, key))
                if 'rc-anchor-alert' in wd.page_source:
                    raise ScraperParseException('Submission of recaptcha token failed')
                else:
                    return True
        else:
            while tries < self.cloudflare_tries():
                tries += 1
                # Check for a flagged value.
                if 'data-translate="checking_browser"' in wd.page_source:
                    self.log.info(
                        'Cloudflare browser check still present after %s tries... '
                        'sleeping.', tries)
                    time.sleep(self.cloudflare_wait())
                else:
                    self.log.info('Passed CF browser check!')
                    break


class UppodDecoderMixin(object):
    """
    Provides a method - decode_uppod - to decode an uppod.swf link for a given
    site.

    https://hms.lostcut.net/viewtopic.php?id=80

    (Replicated in /docs/uppod.decode.txt)

    Basically, decode their uppod.swf file using a transpiler - eg:
    http://www.showmycode.com/

    Look for
    client.codec_a = new array( ... )
    client.codec_b = new array( ... )

    These are per-domain, so will be different for every site.

    Those hashes should be passed into the decode function, along with the value
    we wish to decode.

    """

    def decode(self, value, hash1, hash2):
        # -- define variables
        loc_3 = [0, 0, 0, 0]
        loc_4 = [0, 0, 0]
        loc_2 = ''
        # -- define hash parameters for decoding
        dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

        # -- decode
        for i in range(0, len(hash1)):
            re1 = hash1[i]
            re2 = hash2[i]

            value = value.replace(re1, '___')
            value = value.replace(re2, re1)
            value = value.replace('___', re2)

        i = 0
        while i < len(value):
            j = 0
            while j < 4 and i + j < len(value):
                loc_3[j] = dec.find(value[i + j])
                j += 1

            loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4)
            loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2)
            loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3]

            j = 0
            while j < 3:
                if loc_3[j + 1] == 64:
                    break
                try:
                    loc_2 += unichr(loc_4[j])
                except:
                    pass
                j = j + 1

            i += 4

        return loc_2



class CacheableParseResultsMixin(object):
    """
    This mixin will allow for scraper parse results to be cached for a time, and
    re-submitted.
    This is relevant when a result appears multiple times for either
    single or multiple search terms.
    For instance, we may be searching for "iron" and "man" - this will bring up
    all iron man instances.  The parse action will do the *same thing* for that
    result.
    """
    # 3 hours default (less than our 4 our SLA)
    PR_CACHE_EXPIRY = 60 * 60 * 3

    def _get_cache_key(self, url):
        return 'PARSERESULTS_%s_%s' % (self.__class__.__name__, url)


    def check_for_cached_parse_results(self, parse_url):
        # See if we have any cache results.
        from sandcrawler.scraper.caching import cache
        import redis_cache
        self._pr_cache_key = self._get_cache_key(parse_url)
        try:
            results = cache.get_json(self._pr_cache_key)
        except (redis_cache.ExpiredKeyException,
                redis_cache.CacheMissException):
            self.log.debug('No previously cached results found.')
            self._parse_results = []
            return False
        else:
            # we have old results.
            # Go through and submit them.
            self.log.info('Found cached results for %s - submitting.', parse_url)
            self._submit_cached_parse_results(
                results
            )
            return True


    def parse(self, parse_url, **extra):
        """
        Parse action - scrape and submit OSP links from a site page
        """
        if not self.check_for_cached_parse_results(parse_url):
            return super(CacheableParseResultsMixin, self).parse(
                parse_url, **extra)

    def _submit_cached_parse_results(self, results):
        """
        Actually do the submission of the cached results.

        Calls the super() submit_parse_result, rather than our local
        cached version.
        """
        for result_args, result_kwargs in results:
            super(CacheableParseResultsMixin, self).submit_parse_result(
                *result_args,
                **result_kwargs
            )



    def submit_parse_result(self, *args, **kwargs):
        """
        Takes the parse result and adds to a temporary list, then submits
        properly in the parent function
        """
        if hasattr(self, '_parse_results'):
            self._parse_results.append(
                (args,kwargs)
            )
        return super(CacheableParseResultsMixin, self).submit_parse_result(
            *args,
            **kwargs
        )

    def parse_completed(self):
        """
        When complete, cut in and save our parse results.
        """
        # If we have the __parse_results attributre, we need to cache it.
        if hasattr(self, '_parse_results'):
            from sandcrawler.scraper.caching import cache
            cache.store_json(
                self._pr_cache_key,
                self._parse_results,
                self.PR_CACHE_EXPIRY,
            )

        # Then continue as planned.
        return super(CacheableParseResultsMixin, self).parse_completed()


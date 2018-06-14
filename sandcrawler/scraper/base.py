# -*- coding: utf-8 -*-

import codecs
import logging
import os
import re
import time
import urlparse
import random

import bs4
import requests
import requests.exceptions
from pympler import asizeof

from sandcrawler.scraper.browser import create_simple_driver
from sandcrawler.scraper.exceptions import ScraperParseException, ScraperFetchException, ScraperFetchProxyException, \
    ScraperException
from sandcrawler.scraper.sharedstate import ScraperSharedState
from sandcrawler.scraper.util import ScraperUtil
from sandcrawler.scraper.user_agents import \
    MOBILE_USER_AGENTS, \
    DESKTOP_USER_AGENTS, \
    ALL_USER_AGENTS

class SpecialLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        """
        Overwritten to continue to allow 'extra' passed in as a kwarg.
        """
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update(self.extra)
        return msg, kwargs


class ScraperBase(object):
    """
    The base class for a scraper.

    Scrapers can also share an abstract base class, the manager will determine if a class
    is actually usable if it provides either a `search`, `parse`, or `expand` method.
    """

    URL_TYPE_SEARCH = 'search'          # search()
    URL_TYPE_LISTING = 'listing'        # parse()
    URL_TYPE_AGGREGATE = 'aggregate'    # expand()

    MEDIA_TYPE_TV = 'tv'
    MEDIA_TYPE_FILM = 'film'
    MEDIA_TYPE_GAME = 'game'
    MEDIA_TYPE_BOOK = 'book'
    MEDIA_TYPE_OTHER = 'other'

    MEDIA_TYPE_ALL = (MEDIA_TYPE_TV, MEDIA_TYPE_FILM, MEDIA_TYPE_GAME, MEDIA_TYPE_BOOK, MEDIA_TYPE_OTHER)

    SCRAPER_TYPE_OSP = 'osp'
    SCRAPER_TYPE_P2P = 'p2p'
    ALL_SCRAPER_TYPES = (SCRAPER_TYPE_OSP, SCRAPER_TYPE_P2P)

    # Overridable settings for sanity tests.
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    NO_RESULTS_KEYWORD = 'hhhdddnnn'
    PARSE_RESULTS_FROM_SEARCH = False
    SINGLE_RESULTS_PAGE = False
    ALLOW_FETCH_EXCEPTIONS = False

    # Set this to blanket ovrride to a specific user agent.
    USER_AGENT = None
    # Boolean - whether to allow mobile user agents in the random list.
    USER_AGENT_MOBILE = True
    # Boolean - whether to allow desktop user agents in the random list.
    USER_AGENT_DESKTOP = True

    GET_ATTEMPTS = 2
    GET_RETRY_MIN = 15
    GET_RETRY_MAX = 180

    def __init__(self, *args, **kwargs):
        # Requirements
        self.requires_http_session = True
        self.requires_webdriver = False  # Can be `True` or tuple of form: ('search', 'parse')

        self.search_term_encoding = 'utf-8'
        self.search_term_language = None

        # Webdriver
        self.webdriver_type = 'chrome'  # or phantomjs
        # This will be set later in setup, based on the above  webdriver_type
        # value, which may be overridden in a scraper setup.
        self.driver_url = None

        self.driver_proxy = {}
        self.adblock_enabled = True  # enables adblocking for selenium

        self.proxy_region = None  # if set, the site requires access from a particular region (ISO 3166-1 alpha-3)
        self.no_proxy = False  # Can be `True` or tuple of form: (`search`, `parse`)

        # an optional locking attribute
        self.locking = None

        # Limits
        self.request_limit = 0
        self._requests_performed = 0

        self._request_connect_timeout = 30
        self._request_response_timeout = 60
        self._request_size_limit = (1024 * 1024 * 2)  # Bytes
        self._ignore_chunked_encoding_error = False

        self._webdriver_implicit_wait = 10

        # URLS that we handle
        self._handles_urls = {}

        # Media types that we handle
        self._accepted_media = set()

        # What type of results does this scraper return.
        self._scraper_types = set()

        # Properties
        self._http_session = None
        self._webdriver = None

        # Other bits
        self.log = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        if 'context' in kwargs:
            self.log = SpecialLoggerAdapter(
                logger=self.log,
                extra={
                    'context_uuid': kwargs['context'].get('ctx_uuid'),
                    'module_name': self.__class__.__name__,
                }
            )

        self.util = ScraperUtil()
        self.state = ScraperSharedState(self.__class__.__name__)

        # Results go to this delegate
        self.results_delegate = None

        # Long parses are put on a separate queue so as not to jam everything
        # else up
        self.long_parse = False

        # Logs memory information - heavy operation, but possibly useful!
        self.enable_memory_log = False

        # Call user setup since it's nicer than getting them to override __init__
        self.setup()

        self._record_memory('after setup')

    def _setup(self, *args, **kwargs):
        self._http_session = kwargs.get('http_session', self._http_session)
        self._webdriver = kwargs.get('webdriver', self._webdriver)

        self.webdriver_type = kwargs.get('webdriver_type', self.webdriver_type)
        self.driver_url = kwargs.get('webdriver_address', self.driver_url) or \
            self.webdriver_type
        # if self.driver_url is None:
        #     self.driver_url = 'http://127.0.0.1:8910' \
        #         if self.webdriver_type == 'phantomjs' else 'http://127.0.0.1:9515'

        self.request_limit = kwargs.get('request_limit', self.request_limit)

        self.log = kwargs.get('logger', self.log)

        self.locking = kwargs.get('locking', self.locking)

        self.enable_memory_log = kwargs.get('enable_memory_log',
            self.enable_memory_log)

    #
    # Fetch/scraping transport methods
    #

    def http_session(self):
        if not self._http_session:
            self.log.warning("Warning: creating session")
            self._http_session = requests.Session()

        self._http_session.headers['User-Agent'] = self.get_user_agent()

        return self._http_session

    def get_user_agent(self):
        if not hasattr(self, '_user_agent') or not self._user_agent:
            if self.USER_AGENT:
                self._user_agent = self.USER_AGENT
            else:
                if self.USER_AGENT_DESKTOP and self.USER_AGENT_MOBILE:
                    self._user_agent = random.choice(ALL_USER_AGENTS)
                elif self.USER_AGENT_DESKTOP:
                    self._user_agent = random.choice(DESKTOP_USER_AGENTS)
                elif self.USER_AGENT_MOBILE:
                    self._user_agent = random.choice(MOBILE_USER_AGENTS)
                else:
                    raise NotImplementedError(
                        'USER_AGENT_DESKTOP, USER_AGENT_MOBILE or USER_AGENT '
                        'must be supplied.')
        return self._user_agent

    def webdriver(self):
        if not self.requires_webdriver:
            self.log.error("Error: set `self.requires_webdriver` to True")
            return None

        if not self._webdriver:
            self._webdriver = create_simple_driver(
                self.driver_url,
                adblock=self.adblock_enabled,
                proxy_config=self.driver_proxy,
                page_load_timeout=
                    self._request_connect_timeout + self._request_response_timeout,
                implicit_wait=self._webdriver_implicit_wait,
                user_agent=getattr(self, 'USER_AGENT', None)
            )

        return self._webdriver

    #
    # Class registration
    #

    def register_url(self, url_type, url_regex):
        """
        Declares that the scraper handles a particular URL
        and type of query relating to that URL
        """
        if url_type not in self._handles_urls:
            self._handles_urls[url_type] = []

        self._handles_urls[url_type].append(url_regex)

    def register_media(self, media_type):
        """
        Declares that the scraper handles a particular media type
        """
        if media_type not in self.MEDIA_TYPE_ALL:
            return False

        self._accepted_media.add(media_type)

    def register_scraper_type(self, scraper_type):
        """
        Declares whether the scraper returns OSP and/or P2P links.
        """
        self._scraper_types.add(scraper_type)


    #
    # Querying registration
    #

    def can_handle_type(self, url_type):
        return url_type in self._handles_urls

    def types_for_url(self, url):
        types = set()

        for url_type, urls in self._handles_urls.items():
            for my_url in urls:
                if self.url_matches(my_url, url):
                    types.add(url_type)

        return list(types)

    def urls_for_type(self, typ):
        urls = self._handles_urls.get(typ, [])
        return urls[:]

    @staticmethod
    def url_matches(my_url, other_url):
        # If it's a regex, do a match
        if isinstance(my_url, re._pattern_type):
            return my_url.match(other_url) is not None

        regex = re.compile('^http(s?)://')

        if not regex.match(my_url):
            my_url = "http://" + my_url

        if not regex.match(other_url):
            other_url = "http://" + other_url

        mine = urlparse.urlparse(my_url)
        other = urlparse.urlparse(other_url)

        if mine.path and mine.path != "/" and not other.path.startswith(mine.path):
            return False

        return mine.netloc == other.netloc

    def can_handle_url(self, url, url_type=None):
        if not url_type:
            return self.types_for_url(url) != []

        for my_url in self._handles_urls.get(url_type, []):
            if self.url_matches(my_url, url):
                return True

        return False

    def accepts_media(self, media_type):
        return media_type in self._accepted_media

    #
    # Async results to delegate
    #

    def _desoup_strings(self, dictionary):
        for key, value in dictionary.iteritems():
            if isinstance(value, bs4.NavigableString):
                self.log.debug("Found bs4.NavigableString, converting to Unicode.")
                value = unicode(value)
                dictionary[key] = value

        return dictionary

    def _forward_to_delegate(self, delegate, method_name, *args, **kwargs):
        if not delegate:
            return

        method = getattr(delegate, method_name)
        if not method:
            return

        # Stop memory leaking if any BS strings escaped!
        kwargs = self._desoup_strings(kwargs)

        return method(*args, **kwargs)

    def submit_search_result(self, *args, **kwargs):
        # Cater for a missing domain name.  Links should really be submitted
        # as a full URL, but if just a URI deal with it as best we can.
        for url_field in ('link_url', 'image'):
            # If we don't start with http[s] or don't start with ftp
            # or we're attempting to submit a magnet url.
            if url_field in kwargs and kwargs[url_field] and \
                not (
                    kwargs[url_field].startswith('http') or
                    kwargs[url_field].startswith('ftp') or
                    (ScraperBase.SCRAPER_TYPE_P2P in self._scraper_types and
                     kwargs[url_field].startswith('magnet'))
                ):
                self.log.debug(
                    'Incomplete URL submitted (%s) - attempting to complete',
                    kwargs[url_field]
                )
                if kwargs[url_field].startswith('//'):
                    kwargs[url_field] = 'http:' + kwargs[url_field]
                else:
                    base_url = getattr(self, 'BASE_URL', None)
                    if base_url is None:
                        self.log.warning(
                            "Bad URL submitted without BASE_URL available.")
                    else:
                        if not base_url.endswith('/') and \
                           not kwargs[url_field].startswith('/'):
                            base_url += '/'
                        kwargs[url_field] = base_url + kwargs[url_field]
        self.log.debug("Search result: %s" % kwargs)

        self._forward_to_delegate(self.results_delegate, 'search_result', self.timestamp(), *args, **kwargs)

    def submit_search_no_results(self, *args, **kwargs):
        self.log.debug("Search (no results)")

        self._forward_to_delegate(self.results_delegate, 'search_no_results', self.timestamp(), *args, **kwargs)

    def submit_parse_result(self, *args, **kwargs):
        self.log.debug("Parse result: %s" % kwargs)
        self._forward_to_delegate(self.results_delegate, 'parse_result', self.timestamp(), *args, **kwargs)

    def parse_completed(self, *args, **kwargs):
        self.log.debug("Parse completed: %s" % kwargs)
        self._forward_to_delegate(self.results_delegate, 'parse_completed', self.timestamp(), *args, **kwargs)

    def submit_fetch_error(self, *args, **kwargs):
        self.log.info("Fetch error: %s" % kwargs)
        self._forward_to_delegate(self.results_delegate, 'fetch_error', self.timestamp(), *args, **kwargs)

    def submit_parse_error(self, *args, **kwargs):
        self.log.info("Parse error: %s %s", "".join(args), kwargs)
        self._forward_to_delegate(self.results_delegate, 'parse_error', self.timestamp(), *args, **kwargs)

    #
    # Helper methods for scraper users
    #

    def _record_memory(self, message, extra=None):
        if not self.enable_memory_log:
            return None

        if extra is None:
            extra = {}

        sizer = asizeof.asized(self)
        extra.update({
            'mem_size': sizer.size,
            'mem_flat': sizer.flat
        })
        self.log.info('%s size=%s flat=%s %s' %
                      (self, sizer.size, sizer.flat, message),
                      extra=extra
                      )

    def _request_action(self, action, url, **kwargs):

        self._record_memory('while fetching %s' % url)

        method = getattr(self.http_session(), action)

        # Requests has no content length limit, so stream it in chunks
        # and terminate if we exceed it...
        content = ''
        timeout = (self._request_connect_timeout, self._request_response_timeout)
        r = method(url, timeout=timeout, stream=True, **kwargs)
        try:
            for chunk in r.iter_content(1024):
                content += chunk
                if len(content) > self._request_size_limit:
                    r.close()
                    raise ScraperFetchException('Response size exceeded limit', url=url,
                                                scraper_name=self.__class__.__name__)
        except requests.exceptions.ChunkedEncodingError:
            if not self._ignore_chunked_encoding_error:
                raise
        # Lots of things expect r.content so we underhandedly set it :-)
        r._content = content
        return r

    def _do_request_action(self, action, url, allowed_errors_codes=None, **kwargs):
        try:
            r = self._request_action(action, url, **kwargs)
        except ScraperFetchException as error:
            self.submit_fetch_error(error.message, exception=str(error), url=url)
            error.logged = True
            raise
        except requests.exceptions.ProxyError as error:
            wrapped = ScraperFetchProxyException("Proxy error from requests", error=error, url=url,
                                                 scraper_name=self.__class__.__name__)
            raise wrapped
        except requests.exceptions.RequestException as error:
            self.submit_fetch_error("Exception from requests", exception=str(error), url=url)
            wrapped = ScraperFetchException("Exception from requests", error=error, url=url,
                                            scraper_name=self.__class__.__name__)
            wrapped.logged = True
            raise wrapped

        if r.status_code in (407,):
            raise ScraperFetchProxyException(
                r.reason,
                status_code=r.status_code,
                url=url,
                scraper_name=self.__class__.__name__
            )

        elif r.status_code in (500, 502, 503, 504,):
            raise ScraperFetchProxyException(
                r.reason,
                status_code=r.status_code,
                url=url,
                scraper_name=self.__class__.__name__
            )

        if r.status_code in (301, 302) and \
            'allow_redirects' in kwargs and \
            not kwargs['allow_redirects']:
            return r

        if allowed_errors_codes and \
            r.status_code in allowed_errors_codes:
            return r

        if r.status_code != 200:
            self.submit_fetch_error("Invalid status code", status_code=r.status_code, url=url)
            error = ScraperFetchException(
                r.reason,
                status_code=r.status_code,
                url=url,
                scraper_name=self.__class__.__name__
            )
            error.logged = True
            raise error

        return r

    def _update_request_kwargs(self, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if 'referer' not in kwargs['headers'] and 'Referer' not in kwargs['headers'] and hasattr(self, 'BASE_URL'):
            kwargs['headers']['referer'] = self.BASE_URL
        return kwargs

    def get(self, url, **kwargs):
        attempts = 1
        raise_proxy_errors = kwargs.pop('raise_proxy_errors', False)
        kwargs = self._update_request_kwargs(**kwargs)
        while True:
            try:
                return self._do_request_action('get', url, **kwargs)
            except ScraperFetchProxyException as proxy_error:
                if raise_proxy_errors:
                    raise
                if attempts < self.GET_ATTEMPTS:
                    attempts += 1
                    # 1 - 20 first time\
                    # 1 - 100 last time.
                    delay = random.randint(
                        self.GET_RETRY_MIN,
                        self.GET_RETRY_MAX * attempts
                    )
                    self.log.info(
                        "Proxy error. Retrying after %d seconds: '%s'",
                        delay, url)
                    time.sleep(delay)
                    continue
                else:
                    self.submit_fetch_error("Proxy error", url=url)
                    proxy_error.logged = True
                    raise proxy_error

    def post(self, url, **kwargs):
        kwargs = self._update_request_kwargs(**kwargs)
        return self._do_request_action('post', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs = self._update_request_kwargs(**kwargs)
        return self._do_request_action('head', url, **kwargs)

    def get_redirect_location(self, url, **kwargs):
        kwargs['allow_redirects'] = False
        return self.head(url, **kwargs).headers.get('Location', None)

    def get_soup(self, url, **kwargs):
        result = self.get(url, **kwargs)
        return self.make_soup(result.content, url)

    def post_soup(self, url, **kwargs):
        result = self.post(url, **kwargs)
        return self.make_soup(result.content, url)

    def make_soup(self, content, url=None, from_encoding=None):
        try:
            # Try and unicode it first.
            converted = bs4.UnicodeDammit(
                content
            )
            if converted.unicode_markup:
                content = converted.unicode_markup
            else:
                self.log.warning('Could not convert to unicode: %s', url)
            soup = bs4.BeautifulSoup(content, 'lxml', from_encoding)
            setattr(soup, '_url', url)  # Fudge for debug
        except Exception as error:
            self.submit_parse_error("Parse exception", exception=str(error))
            wrapped = ScraperParseException("Content parse error", error=error, scraper_name=self.__class__.__name__)
            wrapped.logged = True
            raise
        return soup

    def get_soup_for_links(self, soup, search, domain=None, prepend=None):
        """
        Fetch a BS for each link returned for a given search on an existing
        soup, or element thereof.
        """
        for link in soup.select(search):
            href = link['href']
            if prepend:
                href = prepend + href
            if domain and not href.startswith('http'):
                href = domain + href
            if not href.startswith('http'):
                self.log.error('Attempted to soup bad link: %s', href)
                continue
            for soup in self.soup_each([href]):
                yield (link, soup)

    def get_each(self, urls):
        for url in urls:
            try:
                response = self.get(url)
            except ScraperException as error:
                self.log.error("Scraper Error: %s", error)
                continue
            yield response.content

    def soup_each(self, urls):
        for url in urls:
            try:
                soup = self.get_soup(url)
            except ScraperException as error:
                self.log.error("Scraper Error: %s", error)
                continue
            yield soup

    def can_fetch_next(self, increment=True):
        """
        Use this method to query whether you should try and fetch the next page.

        Eg:
            if next_page_link and self.can_fetch_next():
                # Fetch and parse the next page

        This is mainly to be used to aid with search results pages, where lists can be very long,
        and after the first couple of pages, often filled with garbage.
        """


        if self.request_limit == 0:  # No limit
            self.log.debug(
                'can_fetch_next: request_limit=%s requests_performed=%s result=True',
                self.request_limit, self._requests_performed)
            return True

        if increment:
            # Store this as state to keep things simpler from a usage perspective
            self._requests_performed += 1

        if self._requests_performed >= self.request_limit:
            self.log.debug(
                'can_fetch_next: request_limit=%s requests_performed=%s result=False',
                self.request_limit, self._requests_performed)

            return False
        self.log.debug(
            'can_fetch_next: request_limit=%s requests_performed=%s result=True',
            self.request_limit, self._requests_performed)

        return True

    #
    # Empty methods which should be overridden by scrapers
    #

    def setup(self):
        """
        Check for some class variables to initialize.  Note that this method
        can (and often is)  safely overwritten in a subclass.
        """
        # Make sure we have all the *required* parameters.
        for required_attribute in (
            'BASE_URL',
            'SCRAPER_TYPES',
            'LANGUAGE',
            'MEDIA_TYPES',
            'URL_TYPES'
            ):
            if not hasattr(self, required_attribute):
                raise NotImplementedError("Scraper must have %s as a class "
                    "attribute, or implement it's own setup function" %
                    required_attribute)
        # Now go performt these functions.  Note we've already checked
        # the fields exist, so we can just referene them directly.
        for scraper_type in self.SCRAPER_TYPES:
            self.register_scraper_type(scraper_type)

        self.search_term_language = self.LANGUAGE

        for media_type in self.MEDIA_TYPES:
            self.register_media(media_type)

        urls = [ self.BASE_URL,  ]
        if hasattr(self, 'OTHER_URLS'):  # This is not required...
            urls += self.OTHER_URLS
        for url in urls:
            for url_type in self.URL_TYPES:
                self.register_url(url_type, url)

        requires_webdriver = getattr(self, 'REQUIRES_WEBDRIVER', None)
        if requires_webdriver is not None:
            self.requires_webdriver = requires_webdriver
        webdriver_type = getattr(self, 'WEBDRIVER_TYPE', None)
        if webdriver_type is not None:
            self.webdriver_type = webdriver_type

        long_parse = getattr(self, 'LONG_PARSE', None)
        if long_parse is not None:
            self.long_parse = long_parse

    def search(self, search_term, media_type, **extra):
        """
        Search action - search target site for `search_term` and submit site pages as results
        """
        pass

    def parse(self, page_url, **extra):
        """
        Parse action - scrape and submit OSP links from a site page
        """
        pass

    def expand(self, url, **extra):
        """
        Expand action - expand or deobfuscate a URL

        Some links are hidden behind a "multi" page, so this action should return a list of links found.

        In the case of obfuscation, simply return a single item list with the final URL.
        """
        pass

    #
    # Other
    #

    @staticmethod
    def timestamp():
        """
        Simple coarse timestamp
        """
        return int(time.time())

    @staticmethod
    def show_in_browser(html_string_or_soup):
        """
        for debug purposes only

        :param html_string_or_soup: string/soup containing a web page
        :return: opens a browser window
        """
        with codecs.open(os.path.dirname(__file__) + '/~~tmp~~.html', 'w', errors='replace', encoding='UTF-8') as f:
            f.write(unicode(html_string_or_soup)
                    if isinstance(html_string_or_soup, bs4.BeautifulSoup)
                    else html_string_or_soup)
            import webbrowser
            webbrowser.open_new_tab('file://' + f.name)

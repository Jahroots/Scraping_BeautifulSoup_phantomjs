import argparse
import glob
import imp
import inspect
import logging
import os
import sys
import traceback
import random
from urlparse import urlparse

import requests

from sandcrawler.scraper.base import ScraperBase
from sandcrawler.scraper.util import ScraperUtil

SAMPLE_SEARCH_TERMS = {
    ScraperBase.MEDIA_TYPE_FILM: [
        "Annihilation",
        "Daddy's Home 2",
        "Father Figures",
    ],
    ScraperBase.MEDIA_TYPE_TV: [
        "Berlin Station",
        "Brooklyn Nine-Nine"
    ],
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    import rainbow_logging_handler

    handler = rainbow_logging_handler.RainbowLoggingHandler(sys.stderr)
    # handler._column_color['%(asctime)s'] = ('cyan', None, False)
    # handler._column_color['%(levelname)-7s'] = ('green', None, False)
    # handler._column_color['%(message)s'][logging.INFO] = ('blue', None, False)


    handler.setFormatter(
        logging.Formatter("[%(levelname)-5s] [%(name)40s] %(message)s")
    )


    handler.setFormatter(
        logging.Formatter("[%(levelname)-5s] [%(name)40s:%(filename)12s:%(lineno)d] %(message)s")
    )

    # Set 'everything' to INFO
    root = logging.getLogger("")
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # But debug sandcrawler.
    scraperlogger = logging.getLogger('sandcrawler')
    scraperlogger.setLevel(logging.DEBUG)

except:
    # Log everything!
    logging.basicConfig(
        level=logging.DEBUG
    )


class FailedTestException(Exception):
    pass


class PassedTestException(Exception):
    pass


class TestRig(object):
    def __init__(self):

        self.parser = argparse.ArgumentParser()

        self.scraper_class = None

        self.all_scrapers = None

    @property
    def subparsers(self):
        # Use a property so we're added after the first argument group.
        if not hasattr(self, '_subparsers'):
            self._subparsers = self.parser.add_subparsers()
        return self._subparsers

    def add_all_scraper_args(self):
        object_group = self.parser.add_argument_group('scraper')
        object_group.add_argument('filespec',
                                  help='Glob-able specification for scrapers to run')
        object_group.add_argument('--http-proxy', help='HTTP Proxy to use', default=None)
        object_group.add_argument('--page-limit', help='Page fetch limit', default=0, type=int)
        object_group.add_argument('--webdriver-url', help='http url for webdriver.', default=None, type=str)
        object_group.add_argument('endtoend_media_type', choices=list(
            ScraperBase.MEDIA_TYPE_ALL), help='Media type to search')
        object_group.add_argument('endtoend_search_keywords', help='Search '
                                                                   'keywords')

    def add_single_scraper_args(self):
        object_group = self.parser.add_argument_group('scraper')
        object_group.add_argument('file', help='Path to python file containing scraper class')
        object_group.add_argument('classname', help='Class within the file to test')
        object_group.add_argument('--http-proxy', help='HTTP Proxy to use', default=None)
        object_group.add_argument('--page-limit', help='Page fetch limit', default=0, type=int)
        object_group.add_argument('--webdriver-url',
                                  help='http url for webdriver.', default=None,
                                  type=str)

    def add_rediscache_args(self):
        object_group = self.parser.add_argument_group('redis_cache')
        object_group.add_argument('--redis-cache-host',
                                  help='Redis cache host. defaults to blank with no caching.')
        object_group.add_argument('--redis-cache-port',
                                  help='Redis cache port.  Default 6379.', default=6379)

    def add_search_parser_args(self):
        search_parser = self.subparsers.add_parser('search', help='Search '
                                                                  'action')
        search_parser.add_argument('search_media_type', choices=list(ScraperBase.MEDIA_TYPE_ALL),
                                   help='Media type to search')
        search_parser.add_argument('search_keywords', help='Search keywords')

    def add_parse_parser_args(self):

        parse_parser = self.subparsers.add_parser('parse', help='Parse action')
        parse_parser.add_argument('parse_url', help='Page URL')

    def add_endtoend_parser_args(self):
        endtoend_parser = self.subparsers.add_parser('endtoend', help='Search '
                                                                      'then Parse all results')
        endtoend_parser.add_argument('endtoend_media_type', choices=list(ScraperBase.MEDIA_TYPE_ALL),
                                     help='Media type to search')
        endtoend_parser.add_argument('endtoend_search_keywords', help='Search keywords')

    def add_expand_parser_args(self):

        expand_parser = self.subparsers.add_parser('expand', help='Expand '
                                                                  'action')
        expand_parser.add_argument('expand_url', help='Links page URL to expand')

    def add_fulltest_parser_args(self):
        expand_parser = self.subparsers.add_parser('fulltest',
                                                   help='Full test action')

    def validate_single_scraper_args(self):
        self.parser_args = self.parser.parse_args()

        print "Script arguments:", self.parser_args

        if not os.path.isfile(self.parser_args.file):
            print "File not found"
            sys.exit(1)

        # Setup cache before importing any modules.
        self.setup_cache()

        module_path, filename = os.path.split(self.parser_args.file)
        module_name = filename.replace('.py', '')
        module_class = self.parser_args.classname

        try:
            args = imp.find_module(module_name, [module_path])
            scraper_module = imp.load_module(module_name, *args)
        except (ImportError, SyntaxError) as err:
            print "Error loading module file:", err
            traceback.print_exc()
            sys.exit(1)

        if not hasattr(scraper_module, module_class):
            print "Could not find class in module"
            sys.exit(1)

        self.scraper_class = getattr(scraper_module, module_class)

    def validate_all_scraper_args(self):
        self.parser_args = self.parser.parse_args()

    def setup_cache(self):
        if self.parser_args.redis_cache_host:
            from sandcrawler.scraper import caching
            import redis
            connection_pool = redis.ConnectionPool(
                host=self.parser_args.redis_cache_host,
                port=self.parser_args.redis_cache_port,
            )
            caching.cache = caching.RedisCache(connection_pool)
            print 'set cache to : ', caching.cache
        else:
            from sandcrawler.scraper import caching
            caching.cache = caching.FakeCache()

    def _prepare_search_term(self, search_term, scraper=None):
        if scraper is None:
            scraper = self.scraper

        if scraper.requires_webdriver:
            # Selenium seems happier to take in unicode
            term_encoded = search_term
            if isinstance(term_encoded, str):
                term_encoded = term_encoded.decode('utf-8')
        else:
            # Otherwise encode for ease of use with URL strings
            try:
                term_encoded = ScraperUtil.convert(search_term,
                                                   scraper.search_term_encoding)
            except UnicodeEncodeError:
                scraper.log.error("Searcher can't deal with search term")
                return None

        return term_encoded

    def get_setup_scraper_function(self):
        #
        # Setup helpers
        #

        def prepare_session():
            # HTTP Session
            session = requests.Session()
            if self.parser_args.http_proxy:
                session.proxies = {
                    'http': self.parser_args.http_proxy
                }
            return session

        def prepare_webdriver(scraper):
            if scraper.requires_webdriver:
                proxies = {}
                if self.parser_args.http_proxy:
                    proxies['http'] = self.parser_args.http_proxy

                    scraper.driver_proxy = proxies

                if self.parser_args.webdriver_url:
                    scraper.driver_url = self.parser_args.webdriver_url

        def setup_scraper(scraper):
            scraper._setup(
                http_session=prepare_session()
            )
            scraper._setup(request_limit=self.parser_args.page_limit)
            prepare_webdriver(scraper)

        return setup_scraper

    def setup_scraper(self, scraper=None):
        # Create instance
        if scraper is None:
            scraper = self.scraper = self.scraper_class()

        self.get_setup_scraper_function()(scraper)

        return self.scraper

    def run_scraper(self):
        # Perform the action
        action_performed = False
        if getattr(self.parser_args, 'search_keywords', None):
            search_term = self._prepare_search_term(
                self.parser_args.search_keywords,
            )
            self.scraper.search(search_term, self.parser_args.search_media_type)
            action_performed = True
        elif getattr(self.parser_args, 'parse_url', None):
            self.scraper.parse(self.parser_args.parse_url)
            self.scraper.parse_completed()
            action_performed = True
        if getattr(self.parser_args, 'endtoend_search_keywords', None):
            self.run_end_to_end()
            action_performed = True
        elif getattr(self.parser_args, 'expand_url', None):
            results = self.scraper.expand(self.parser_args.expand_url)
            action_performed = True
            print "Results", results

        if not action_performed:
            self.run_full_test()

    def run_end_to_end(self):
        scrape_class = self.scraper_class
        setup_scraper = self.setup_scraper

        class EndToEndDelegate(object):
            def __init__(self):
                self.num_search_results = 0
                self.num_search_noresults = 0
                self.num_parse_results = 0
                self.num_parse_errors = 0
                self.num_fetch_errors = 0

            def search_result(self, timestamp, **kwargs):
                logger.debug('Search result: %s', kwargs)
                self.num_search_results += 1
                url = kwargs.get('link_url', None)
                if url:
                    obj = scrape_class()  # clone
                    setup_scraper(scraper=obj)
                    obj.parse(url)
                    obj.parse_completed()

            def search_no_results(self, timestamp, *args, **kwargs):
                logger.debug('Got search_no_results')
                self.num_search_noresults += 1

            def parse_result(self, timestamp, *args, **kwargs):
                logger.debug('Parse result: %s', kwargs)
                self.num_parse_results += 1

            def fetch_error(self, timestamp, *args, **kwargs):
                logger.warning('Fetch error')
                self.num_fetch_errors += 1

            def parse_error(self, timestamp, *args, **kwargs):
                logger.warning('Parse error')
                self.num_parse_errors += 1

        self.scraper.results_delegate = EndToEndDelegate()

        search_term = self.parser_args.endtoend_search_keywords
        search_term = self._prepare_search_term(search_term)

        self.scraper.search(search_term, self.parser_args.endtoend_media_type)

    def run_full_test(self):
        scrape_class = self.scraper_class
        setup_scraper = self.setup_scraper

        MAX_PARSE_RESULTS = 10

        class FullTestDelegate(object):

            def __init__(self, scraper_factory):
                self.scraper_factory = scraper_factory
                self.scraper = scraper_factory()
                # Limit the scraper amount here.
                self.scraper.request_limit = 2
                self.num_search_results = 0
                self.num_search_noresults = 0
                self.num_parse_results = 0
                self.num_parse_errors = 0
                self.num_fetch_errors = 0

            def __validate_url(self, url):
                if ScraperBase.SCRAPER_TYPE_P2P in self.scraper._scraper_types and \
                    url.startswith('magnet'):
                    # TODO - more validation?
                    return True

                if not url or not isinstance(url, basestring):
                    raise FailedTestException('Invalid url submitted: %s (type is %s)' % (url, str(type(url))))
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    raise FailedTestException('Invalid url submitted: %s' % url)

            def __validate_search_url(self, url):
                self.__validate_url(url)
                passed = False
                # make sure the url would be covered by our registered urls.
                for my_url in self.scraper._handles_urls.get(
                        self.scraper.URL_TYPE_LISTING, []):
                    if self.scraper.url_matches(my_url, url):
                        passed = True
                        break
                if not passed:
                    raise FailedTestException(
                        u'URL {} would not be handled by parse '
                        u'(hint: check www.)'.format(url))

            def search_result(self, timestamp, **kwargs):
                self.num_search_results += 1
                url = kwargs.get('link_url', None)
                self.__validate_search_url(url)
                image = kwargs.get('image', None)
                if image:
                    self.__validate_url(image)
                if url and self.num_parse_results <= MAX_PARSE_RESULTS:
                    try:
                        scraper = self.scraper_factory()
                        scraper.results_delegate = self
                        scraper.parse(url)
                        scraper.parse_completed()
                    except PassedTestException:
                        pass

            def search_no_results(self, timestamp, *args, **kwargs):
                logger.debug('No search no results')
                self.num_search_noresults += 1

            def parse_result(self, timestamp, *args, **kwargs):
                logger.debug('Parse result: %s', kwargs)
                url = kwargs.get('link_url', None)
                self.__validate_url(url)
                image = kwargs.get('image', None)
                if image:
                    self.__validate_url(image)
                self.num_parse_results += 1
                # Only bother with 10 parse results; catch this in our search
                # result function
                if self.num_parse_results > MAX_PARSE_RESULTS and \
                        not self.scraper.PARSE_RESULTS_FROM_SEARCH:
                    raise PassedTestException('Received 10 parse results.')

            def fetch_error(self, timestamp, *args, **kwargs):
                logger.warning('Fetch error')
                if not self.scraper.ALLOW_FETCH_EXCEPTIONS:
                    raise FailedTestException(
                        'Fetch error.  Check url/site availability.')

            def parse_error(self, timestamp, *args, **kwargs):
                logger.warning('Parse error')
                self.num_parse_errors += 1
                raise FailedTestException(
                    'Fetch error.  Check url/site availability.')

            def parse_completed(self, timestamp):
                return

        # Just do 3 pages for the sake of not sitting around for 100 pages of
        # results
        passed = []
        failed = []
        self.scraper.request_limit = 2
        for media in self.scraper._accepted_media:
            for raw_search_term in SAMPLE_SEARCH_TERMS.get(media, []) + [self.scraper.LONG_SEARCH_RESULT_KEYWORD]:
                try:
                    self.scraper.results_delegate = FullTestDelegate(
                        self.setup_scraper
                    )
                    logger.info('Searching %s for %s - %s (Looking for results)',
                        self.scraper, raw_search_term, media)

                    search_term = self._prepare_search_term(raw_search_term)
                    self.scraper.search(search_term, media)

                    # Validate our results.
                    if not self.scraper.PARSE_RESULTS_FROM_SEARCH and \
                                    self.scraper.results_delegate.num_search_results == 0:
                        raise FailedTestException('No search results found for %s' %
                                                  search_term)
                    if self.scraper.results_delegate.num_parse_results == 0:
                        raise FailedTestException('No parse results found for %s' %
                                                  search_term)
                    if self.scraper.results_delegate.num_search_noresults > 0:
                        raise FailedTestException('Received search no results for %s' %
                                                  search_term)
                    if search_term == self.scraper.LONG_SEARCH_RESULT_KEYWORD and \
                        self.scraper.results_delegate.scraper._requests_performed == 0 and \
                        not self.scraper.SINGLE_RESULTS_PAGE:
                        raise FailedTestException(
                            'Only fetched a single search result page.'
                        )
                except FailedTestException, e:
                    failed.append((search_term, media, e))
                else:
                    passed.append((search_term, media))


        # Other tests...?
        # Reset and do our no results test
        try:
            self.scraper.results_delegate = FullTestDelegate(
                self.setup_scraper
            )
            self.scraper._requests_performed = 0
            search_term = self.scraper.NO_RESULTS_KEYWORD
            search_term = self._prepare_search_term(search_term)

            media = list(self.scraper._accepted_media)[0]
            logger.info('Searching %s for %s - %s (Looking for no results)',
                self.scraper, self.scraper.NO_RESULTS_KEYWORD,
                media)

            self.scraper.search(search_term, media)

            if self.scraper.results_delegate.num_search_results or \
                    self.scraper.results_delegate.num_parse_results:
                raise FailedTestException(
                    'Received search results for %s' % search_term)
            if not self.scraper.results_delegate.num_search_noresults:
                raise FailedTestException(
                    'Did not receive search no results for %s' % search_term)
            if self.scraper._requests_performed > 1:
                raise FailedTestException(
                    'Fetched multiple pages for %s' % search_term)
        except FailedTestException, e:
            failed.append((search_term, media, e))
        else:
            passed.append((search_term, media))


        if len(passed) == 0:
            logger.error('All tests failed!')
        elif len(failed):
            logger.warning('%s/%s tests failed.  Please review failed keywords.', len(failed), len(passed) + len(failed))
            for failed in failed:
                logger.info('Search for "%s" (%s) failed: %s' % failed)
        else:
            logger.info('All tests passed')


    @staticmethod
    def is_overridden(base_class, other_class, method_name):
        base_method = getattr(base_class, method_name)
        other_method = getattr(other_class, method_name)
        return base_method.__func__ is not other_method.__func__

    def _validate_scraper_class(self, klass):
        # IMPROVE: Flesh this out more as the framework matures
        if not issubclass(klass, ScraperBase):
            return False

        if klass == ScraperBase:
            return False

        if not self.is_overridden(ScraperBase, klass, 'setup'):
            return False

        return True

    def _find_scrapers_in_module(self, module):
        # Bastardisation of scrapermanager.get_scraper_classes.

        found = set()

        # Inspect the module and grab all classes for potential inclusion
        scraper_classes = []
        for thing_name in dir(module):
            thing = getattr(module, thing_name)
            if inspect.isclass(thing):
                scraper_classes.append(thing)

        # Filter/validate, etc
        for scraper_class in scraper_classes:
            if self._validate_scraper_class(scraper_class):
                found.add(scraper_class)

        return list(found)

    def setup_all_scrapers(self):

        self.all_scrapers = []

        for filename in glob.glob(self.parser_args.filespec):
            if filename.endswith('.py') and filename != "__init__.py":
                module_path, filename = os.path.split(filename)
                module_name = filename.replace('.py', '')
                try:
                    args = imp.find_module(module_name, [module_path])
                    module = imp.load_module(module_name, *args)
                    self.all_scrapers += self._find_scrapers_in_module(
                        module)
                except (ImportError, SyntaxError) as err:
                    print "Error loading module file:", err
                    traceback.print_exc()
                    sys.exit(1)

        print "Found %s scraper classes..." % (len(self.all_scrapers))

    def run_all_scrapers(self):

        # Consider dropping logging down; this can get noisey.
        # logger.getLogger().setLevel(logger.DEBUG)
        for scraper_class in self.all_scrapers:
            logger.warning('Running %s', scraper_class)
            self.scraper_class = scraper_class
            self.setup_scraper()
            self.run_end_to_end()
            for key in (
                    'num_search_results',
                    'num_search_noresults',
                    'num_parse_results',
                    'num_parse_errors',
                    'num_fetch_errors',
            ):
                logger.warning('%s: %s',
                             key, getattr(self.scraper.results_delegate, key))


def test_script_main():
    """
    Rigs up a scraper module and performs actions via the command line
    """

    testrig = TestRig()

    testrig.add_single_scraper_args()

    testrig.add_search_parser_args()
    testrig.add_parse_parser_args()
    testrig.add_endtoend_parser_args()
    testrig.add_expand_parser_args()
    testrig.add_fulltest_parser_args()
    testrig.add_rediscache_args()

    testrig.validate_single_scraper_args()

    testrig.setup_scraper()

    testrig.run_scraper()


def test_script_all():
    """
    Sets up the test rig to end-to-end *all* scrapers.
    """
    testrig = TestRig()
    testrig.add_all_scraper_args()
    testrig.add_rediscache_args()
    # testrig.add_endtoend_parser_args()
    testrig.validate_all_scraper_args()

    testrig.setup_all_scrapers()
    testrig.run_all_scrapers()

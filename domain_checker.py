#!/usr/bin/env python2.7

import sys
import os
import glob
import imp
import inspect
import traceback
import logging
import requests
import argparse
import csv
from urlparse import urlparse

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

# Scrapers import from 'scraper'
sys.path.append('sandcrawler')

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import extras

class DomainChecker(object):
    """
    Goes through all scrapers, builds an object, and tries a .get (which may
    include cloudlfare, etc) and checks for redirects, etc.
    """

    def __init__(self, globspec, user_agent, skip, outputfile):
        # Setup a list of bases that are NOT scrapers (generally parents of)
        self.IGNORE_BASES = []
        for possible_base_name in dir(extras):
            possible_base = getattr(extras, possible_base_name)
            if inspect.isclass(possible_base) and \
                issubclass(possible_base, ScraperBase):
                self.IGNORE_BASES.append(possible_base)

        # A generic session with a believable user agent...
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent
        self.globspec = 'scrapers/{}'.format(globspec)
        self.skip = skip
        self.outputfile = outputfile

        # Blank caches...
        from sandcrawler.scraper import caching
        caching.cache = caching.FakeCache()

    def _get_scrapers_in_module(self, module):
        # Inspect the module and grab all classes for potential inclusion
        for thing_name in dir(module):
            thing = getattr(module, thing_name)
            if inspect.isclass(thing) and \
                issubclass(thing, ScraperBase) and \
                thing not in self.IGNORE_BASES:
                yield thing


    def get_all_scrapers(self):

        for filename in sorted(glob.glob(self.globspec))[self.skip:]:
            if not filename.startswith('scrapers/_'):
                module_path, filename = os.path.split(filename)
                module_name = filename.replace('.py', '')
                try:
                    args = imp.find_module(module_name, [module_path])
                    module = imp.load_module(module_name, *args)

                    for scraper_class in self._get_scrapers_in_module(module):
                        try:
                            scraper = scraper_class()
                        except NotImplementedError:
                            logger.info('%s raises not implemented.', scraper_class)
                            continue
                        scraper._setup(http_session=self.session)
                        yield scraper, filename
                except (ImportError, SyntaxError) as err:
                    print "Error loading module file:", err
                    traceback.print_exc()


    def run(self):
        """
        Fetch each url and check whether it is still valid.
        """
        logger.info('Loading scrapers...')
        results = []
        try:
            for scraper, filename in self.get_all_scrapers():
                run_command = './scraper-run ./scrapers/{} {} fulltest'.format(
                    filename, scraper.__class__.__name__
                )
                base_url = getattr(scraper, 'BASE_URL')
                if not base_url:
                    scraper.log.warning('%s: Could not fetch - no BASE_URL',
                        scraper)
                    continue
                logger.info('%s: Fetching %s', scraper, base_url)
                try:
                    response = scraper.get(
                        base_url,
                        allow_redirects=False,
                        raise_proxy_errors=True,
                    )
                except Exception, e:
                    logger.exception('Error fetching %s', base_url)
                    results.append(
                        (scraper.__class__.__name__, base_url, 'FAILURE',
                         str(e))
                    )
                else:
                    if response.is_redirect:
                        destination = response.headers.get('Location')
                        if not destination:
                            results.append(
                                (scraper.__class__.__name__,
                                 base_url,
                                 'REDIRECT',
                                 'NO DESTINATION GIVEN',
                                 run_command,
                                 )
                            )
                        else:
                            parsed_base = urlparse(base_url)
                            parsed_destination = urlparse(destination)
                            if parsed_base.netloc != parsed_destination.netloc or \
                                parsed_base.scheme != parsed_destination.scheme:
                                results.append(
                                    (scraper.__class__.__name__,
                                     base_url,
                                     'REDIRECT',
                                     destination,
                                     run_command
                                     )
                                )
                            else:
                                results.append(
                                    (scraper.__class__.__name__,
                                     base_url,
                                     'OK',
                                     response.url,
                                     run_command,
                                     )
                                )
                    elif response.ok:
                        results.append(
                            (scraper.__class__.__name__, base_url, 'OK', '', run_command,)
                        )
                    else:
                        results.append(
                            (scraper.__class__.__name__, base_url, 'ERROR', response.status_code, run_command)
                        )
                logger.info(results[-1])
        finally:
            with open(self.outputfile, 'wb') as f:
                outputcsv = csv.writer(f)
                outputcsv.writerow(['Scraper', 'BASE_URL', 'Status', 'Notes', 'Run'])
                outputcsv.writerows(results)
            logger.info('Outputted to %s', self.outputfile)




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--glob',
        help='Glob-able specification for scrapers to check (eg *ru.py)',
        default='*.py'
    )
    parser.add_argument(
        '--user_agent',
        help='Override for default user agent.',
        default='Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/' \
                '20121011 Firefox/16.0.1',
    )

    parser.add_argument(
        '--skip',
        help='Skip first X scrapers (note - scrapers are alphabetical based on FILENAME)',
        type=int,
        default=0,
    )

    parser.add_argument(
        '--outputfile',
        help='Results output file.',
        default='results.csv',
    )



    args = parser.parse_args()
    DomainChecker(
        args.glob,
        args.user_agent,
        args.skip,
        args.outputfile
    ).run()





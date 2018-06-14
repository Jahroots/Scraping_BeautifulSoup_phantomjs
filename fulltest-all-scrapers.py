# -*- coding: utf-8 -*-
# !/usr/bin/env python2.7

import logging as log
import os
import sys
from collections import OrderedDict
from subprocess import call
from sys import executable


# skip already tested and
START_FROM = ''  # format is like 'bestkino_su' (modulename) OR BestKinoSU (classname)

# LONG_SEARCH_RESULT_KEYWORD = '2015'
# SINGLE_RESULTS_PAGE = True

try:
    import rainbow_logging_handler

    handler = rainbow_logging_handler.RainbowLoggingHandler(sys.stderr)
    handler._column_color['%(asctime)s'] = ('cyan', None, False)
    handler._column_color['%(levelname)-7s'] = ('green', None, False)
    handler._column_color['%(message)s'][log.INFO] = ('white', None, False)

    handler.setFormatter(log.Formatter("%(levelname)-5s %(message)s"))

    root = log.getLogger("")
    root.addHandler(handler)
    root.setLevel(log.DEBUG)
except:
    # Log everything!
    log.basicConfig(level=log.DEBUG)


def test_it(scraper_module_, cls_):
    log.warning('./scraper-run --redis-cache-host=127.0.0.1 ./scrapers/' + scraper_module_ + ' ' + cls_ + ' fulltest')
    call([executable, os.path.abspath('.') + '/scraper-run', '--redis-cache-host=127.0.0.1',
          'scrapers/' + scraper_module_, cls_, 'fulltest'])


scraper_modules_and_classes = OrderedDict()
for scraper in sorted(os.listdir(os.path.abspath('.') + '/scrapers')):

    if not scraper.startswith('_') and scraper.endswith('.py'):
        scraper_modules_and_classes[scraper] = []

        for cls in (row.split('class ')[1].split('(')[0] for row in
                    open(os.path.abspath('.') + '/scrapers/' + scraper) if row.startswith('class ')):
            scraper_modules_and_classes[scraper].append(cls)

for scraper_module, scraper_classes in scraper_modules_and_classes.items():

    if START_FROM and (scraper_module[:-3] != START_FROM and START_FROM not in scraper_classes):
        log.warning('({}) skipping until {}'.format(scraper_module, START_FROM))
        continue

    log.info('\n@@@@@@@@@@@@@@@ ' + scraper_module + ' @@@@@@@@@@@@@@@')

    for cls in scraper_classes:
        log.debug('       ' + cls)
        if START_FROM and START_FROM != cls:
            log.warning('    ({}) skipping until {}'.format(scraper_module, START_FROM))
            continue

        START_FROM = ''

        test_it(scraper_module, cls)

        while raw_input('\n˜˜˜˜˜˜˜˜˜˜˜˜finished {}.{}˜˜˜˜˜˜˜˜˜˜˜˜\n\n***r*to*repeat,*enter*for         NEXT? > \a\a'.format(
                scraper_module, cls)).startswith(('r', 'R')):
            log.warning('REPEATING ' + repr(((scraper_module, cls))))
            test_it(scraper_module, cls)

# https://docs.google.com/spreadsheets/d/1533kpBuHIFo2ly44PAA4ttVnYukRVTiZ9wfsF5n7v9Y/edit#gid=0

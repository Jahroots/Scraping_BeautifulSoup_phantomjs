#!/usr/bin/env python2.7


import sys
import os
import requests
from urlparse import urlparse
from urllib import urlencode
import tld
from bs4 import BeautifulSoup
import subprocess

# Scrapers import from 'scraper'
sys.path.append('sandcrawler')

class Builder(object):
    """
    Builds a best try scraper based on some user provided variables, and some
    simple deductions.

    Note that the results will generally not be a completed scraper, but will
    atleast give a basis to work from.
    """

    TEMPLATE = 'scraper_template.tmpl'
    SCRAPERS = './scrapers/'

    API_KEY = '7f29c06bed146f83ab0a061ba0f3df67e9b0f90a'
    API_BASE_URI = 'http://access.alchemyapi.com/calls'

    API_CALL_URI = '{0}/url/URLGetLanguage?apikey={1}&outputMode=json&url='.format(API_BASE_URI, API_KEY)
    USER_AGENT_DEFAULT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537'

    def __init__(self):
        # Initialize required vars to None.
        self.domain_name = None
        self.file_name = None
        self.module_name = None
        self.language = None
        self.user_agent = None

        # And some (sane?) defaults for others.
        self.has_search = True
        self.has_listing = True

        self.is_osp = True
        self.is_p2p = False

        self.is_film = True
        self.is_tv = True
        self.is_games = False
        self.is_book = False
        self.is_other = False

        self.extra_imports = ['SimpleScraperBase', ]
        self.module_bases = ['SimpleScraperBase', ]

        self.search_url = self.search_url_unformatted = ''
        self.next_button_identifier = \
            self.search_result_identifier = \
            self.parse_result_identifier = ''


        # And some other vars...
        self.session = requests.Session()
        self.home_body = None

    # Input helpers.
    def _input_to_bool(self, question, default):
        response = raw_input(question)

        if response == '':
            return default
        if response in ['Y', 'y', 'Yes', 'T', 'True']:
            return True
        return False

    def _check_url_lang(self, url):

        # Do api thing.
        try:
            response = requests.get(self.API_CALL_URI + url)
            return response.json()['iso-639-2']
        except KeyError, e:
            print 'Unable to get language.'
            return 'TODO'

    def check_for_existing_scraper(self):
        # Check for whether this domain exists.
        domain = tld.get_tld(self.domain_name, as_object=True).domain

        cmd = 'grep -i "{}" {}*'.format(
            domain, self.SCRAPERS
        )
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        contents = process.communicate()[0]

        if contents:
            print 'The following other files were found that may already have' \
                  'that scraper:'
            print '-' * 30
            print contents
            print '-' * 30
            if not self._input_to_bool(
                'Would you like to continue? [Y/N] (default N)',
                False
                ):
                sys.exit(0)

    def check_and_propagate_domain(self):
        print 'Checking domain name: %s' % self.domain_name
        # First make sure it's a valid domain
        parsed = urlparse(self.domain_name)
        if not parsed.netloc:
            print 'Invalid domain'
            sys.exit(1)
        if not parsed.scheme:
            print 'No scheme provided'
            sys.exit(1)
        if (parsed.path and parsed.path != '/') or parsed.query:
            print 'Please just include the domain name - no path/query info.'
            sys.exit(1)

        self.domain_name = self.domain_name.rstrip('/')

        self.check_for_existing_scraper()

        # Now try a request.
        response = self.session.get(
            self.domain_name,
            allow_redirects=False,
        )
        if response.is_redirect:
            location = response.headers.get('Location')
            if location:
                # See if it's still on the same domain
                location_parsed = urlparse(location)
                if location_parsed.netloc == parsed.netloc:
                    print '...Domain root redirected to {}'.format(location)
                    # Note this only allows a single redirect...
                    response = self.session.get(
                        location,
                        allow_redirects=False
                    )
                else:
                    print 'Domain {} redirects to a different domain: {}'.format(
                        self.domain_name, location)
                    sys.exit(1)
            else:
                print 'Domain is a redirect to unknown location...'
                sys.exit(1)
        if response.ok:
            # Try a user agent.
            print '...Non-OK response - trying with user agent.'
            response = self.session.get(
                self.domain_name,
                headers={
                    'User-Agent': self.USER_AGENT_DEFAULT
                }
            )
            if response.ok:
                self.user_agent = self.USER_AGENT_DEFAULT
            else:
                # TODO - check for cloudflare, include as a mixin.
                # TODO - check other urser agents and include a replacement get/post super call.
                import ipdb; ipdb.set_trace()
                print 'Invalid response; %s' % response
                sys.exit(1)

        # We good!  Lets populate some of our info
        self.home_body = response.content
        self.soup = BeautifulSoup(self.home_body, 'lxml')

        # Set the (default...) language
        self.language = self._check_url_lang(self.domain_name)

        short_netloc = parsed.netloc
        if short_netloc.startswith('www.'):
            short_netloc = short_netloc[4:]

        self.file_name = os.path.join(
            self.SCRAPERS,
            short_netloc.replace('.', '_').replace('-', '_') + '.py'
        )

        self.module_name = ''
        cap_next = True
        for letter in short_netloc:
            if letter in '-._':
                cap_next = True
            else:
                if cap_next:
                    self.module_name += letter.upper()
                else:
                    self.module_name += letter
                cap_next = False



    def locate_search_form(self):
        search_form = search_input = None
        # First see if we can find a form.
        for search_string in [
            'form#search',
            'form.search',
            'form.search-form',
        ]:
            search_form = self.soup.select_one(search_string)
            if search_form:
                break
        if not search_form:
            # See if we can find an input that looks right.
            for search_string in [
                'input.search',
                'input.search-field',
                'input.searchinput',
                'input#search',
                'input#search-input',
                'input#submitSearch',
                'input[name="q"]',
                'input[name="s"]',

            ]:
                search_input = self.soup.select_one(search_string)
                if search_input:
                    break
            if search_input:
                # Go up and find our form.
                search_form = search_input.find_parent('form')

        if not search_form:
            print 'Could not find a search form.'
            return None

        # Make sure it's a GET.
        # TODO - modify simplescraperbase to handle a POST search
        method = search_form.get('method', 'get')
        if method.upper() != 'GET':
            print 'Cannot handle POST searches, yet.'
            return

        # Check the action.
        search_action = search_form.get('action', '')
        if search_action:
            if search_action.startswith('http') and \
                not search_action.startswith(self.domain_name):
                # TODO - SimpleGoogleScraper?
                print 'Search action is %s - cannot handle.' % search_action
                return

        search_action = urlparse(search_action).path

        query_values = {}
        search_field_name = ''
        # Go through and find all fields.
        for field in search_form.select('input'):
            field_name = field.get('name')
            if not field_name:
                continue
            if field.get('type', '') == 'text' and field.get('value', '') == '':
                # This is the search field...
                search_field_name = field_name
            else:
                query_values[field_name] = field.get('value', '')

        query_params = urlencode(query_values)

        self.search_url_unformatted = """{{base_url}}{}?{}&{}={{search_term}}""".format(
            search_action,
            query_params,
            search_field_name,
        )

        self.search_url = "'{}'.format(" \
            "base_url=self.BASE_URL, search_term=search_term)"\
            .format(self.search_url_unformatted)


    def run(self):
        if len(sys.argv) > 1:
            self.domain_name = sys.argv[1]
        else:
            self.domain_name = raw_input('Enter base url: ')
        self.check_and_propagate_domain()
        self.locate_search_form()

        self.language = raw_input(
            'Site language ISO Code (default %s)' % self.language
        ) or self.language


        self.is_osp = self._input_to_bool(
            'Is this an OSP (Streaming/Download) site? [Y/N] (default Y)',
            True
        )
        self.is_p2p = self._input_to_bool(
            'Is this a P2P (Bittorrent) site? [Y/N] (default N)',
            False
        )

        self.is_film = self._input_to_bool(
            'Is this a FILM site? [Y/N] (default Y)',
            True
        )
        self.is_tv = self._input_to_bool(
            'Is this a TV site? [Y/N] (default Y)',
            True
        )
        self.is_games = self._input_to_bool(
            'Is this a GAME site? [Y/N] (default N)',
            False
        )

        self.is_book = self._input_to_bool(
            'Is this a BOOK site? [Y/N] (default N)',
            False,
        )
        self.is_other = self._input_to_bool(
            'Is this an OTHER site? [Y/N] (default N)',
            False,
        )

        self.no_results_text = raw_input(
            'Enter a No Results Text.  (default TODO)'
        ) or ' TODO '

        self.next_button_identifier = raw_input(
            'Enter a BeautifulSoup css path for NEXT BUTTON.  (default TODO)'
        ) or ' TODO '

        self.search_result_identifier = raw_input(
            'Enter a BeautifulSoup css path for SEARCH RESULTS.  (default TODO)'
        ) or ' TODO '

        self.parse_result_identifier = raw_input(
            'Enter a BeautifulSoup css path body of PARSE RESULTS.  (default TODO)'
        ) or ' TODO '

    def output(self):

        print 'Outputting %s to %s' % (self.module_name, self.file_name)

        input_template = open(self.TEMPLATE, 'r').read()

        extra_imports = ''
        if self.extra_imports:
            extra_imports = ', ' + ', '.join(self.extra_imports)

        module_bases = ', '.join(self.module_bases)

        scraper_types = []
        if self.is_osp:
            scraper_types.append('ScraperBase.SCRAPER_TYPE_OSP')
        if self.is_p2p:
            scraper_types.append('ScraperBase.SCRAPER_TYPE_P2P')

        media_types = []
        if self.is_film:
            media_types.append('ScraperBase.MEDIA_TYPE_FILM')
        if self.is_tv:
            media_types.append('ScraperBase.MEDIA_TYPE_TV')
        if self.is_book:
            media_types.append('ScraperBase.MEDIA_TYPE_BOOK')
        if self.is_games:
            media_types.append('ScraperBase.MEDIA_TYPE_GAME')
        if self.is_other:
            media_types.append('ScraperBase.MEDIA_TYPE_OTHER')

        output =  input_template.format(
            extra_imports=extra_imports,
            module_name=self.module_name,
            module_bases=module_bases,
            base_url=self.domain_name,
            scraper_types=', '.join(scraper_types),
            language=self.language,
            media_types=', '.join(media_types),
            search_url=self.search_url,
            no_results_text=self.no_results_text,
            fetch_next_button=self.next_button_identifier,
            search_result_identifier=self.search_result_identifier,
            parse_result_identifier=self.parse_result_identifier,
        )

        if os.path.exists(self.file_name):
            if self._input_to_bool(
                    'A scraper already exists at {} - ovewrite? [Y/N] '
                    '(default N)'.format(self.file_name),

                    False):
                os.remove(self.file_name)
            else:
                sys.exit(1)

        with open(self.file_name, 'w') as f:
            f.write(output)


        cmd = 'git add {}'.format(self.file_name)
        subprocess.Popen(cmd, shell=True)

        print '** Scraper outputted to %s and added to git.' % self.file_name
        print 'python ./scraper-run {} {} fulltest'.format(
            self.file_name, self.module_name)



if __name__ == '__main__':
    builder = Builder()
    builder.run()
    builder.output()

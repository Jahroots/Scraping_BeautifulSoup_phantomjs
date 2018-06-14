# coding=utf-8

from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin, ScraperAuthException


class DarkWarezPL(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'http://darkwarez.pl'

    USERNAME = 'Eark1987'
    PASSWORD = 'kuS7em8Pie'
    # Note - this site blocks fakenamegenerator emails.
    EMAIL = 'KathleenRLyman@myspoonfedmonkey.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "pol"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          self.BASE_URL)

        self.no_proxy = ('search',)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _login(self):
        self.log.debug('Logging in...')
        login_result = self.post(self.BASE_URL + '/forum/login.php',
                                 data={
                                     'usrname': self.USERNAME,
                                     'passwrd': self.PASSWORD,
                                     'redirect': 'search.php',
                                     'login': 'Zaloguj'
                                 }
                                 )
        # Check for the failed login text.
        if login_result.text.find(
                u'Podałeś nieprawidłowe lub nieaktywne dane użytkownika'
        ) >= 0:
            raise ScraperAuthException('Failed login with %s / %s')
            # otherwise, we good.

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.post_soup(
            self.BASE_URL + '/forum/search.php?mode=results',
            data={
                'search_keywords': self.util.quote(search_term),
                'only_topics': 'topics',
                'search_terms': 'all',
                'search_author': '',
                'search_forum': 5,  # Movies section.
                'search_time': 0,
                'search_cat': 1,
                'sort_by': 0,
                'sort_dir': 'DESC',
                'show_results': 'topics',
                'return_chars': 1000
            })
        self._find_search_links(soup)
        # Then go find our 'next' links.
        self._iterate_next_links(
            soup, self._find_search_links
        )

    def _find_search_links(self, soup):
        found = False
        for page_link in soup.select('a.topictitle'):
            full_url = self.util.canonicalise(
                self.BASE_URL,
                '/forum/' + page_link.get('href')
            )
            self.submit_search_result(link_title=page_link.text,
                                      link_url=full_url,
                                      )
            found = True
        if not found:
            self.submit_search_no_results()

    def _iterate_next_links(self, soup, callback):
        next_link = soup.find('a', text=u'Następna')
        while next_link and self.can_fetch_next():
            next_url = self.util.canonicalise(
                self.BASE_URL,
                '/forum/' + next_link.get('href')
            )
            soup = self.get_soup(next_url)
            callback(soup)
            next_link = soup.find('a', text=u'Następna')

    def parse(self, page_url, **extra):
        self._login()

        soup = self.get_soup(page_url)

        title = soup.title.text

        for code_block in soup.select('td.code'):
            while True:
                if code_block.p:
                    code_block.p.decompose()
                else:
                    break
            # Special case for egofiles
            # http&#58;//egofies upadlo/3B56BPllgkhHlPlY/Mother.and.Child.2009.PL.BRRiP.Xvid-MX.avi
            search_text = unicode(code_block.text) \
                .replace('<!-- .xup.pl/ -->', '') \
                .replace('egofies upadlo', 'egofiles.com')

            for i, link in enumerate(self.util.find_urls_in_text(
                    search_text, skip_images=True)
            ):

                if 'xup.pl' in link:
                    link = link.replace('.ul.xup.pl', '.uploaded.xup.pl')
                    http, _, dom, rest = link.split('/', 3)
                    dom = dom.split('.')[1]
                    upload_sites = dict(extabit='com',
                                        catshare='net',
                                        rapidgator='net',
                                        storbit='net',
                                        rapidu='net',
                                        uploaded='net',
                                        turbobit='net',
                                        fileshark='pl',
                                        lunaticfiles='com',
                                        rapidshare='com',
                                        depositfiles='com',
                                        hotfile='com',
                                        jumbofiles='com',
                                        bitshare='com',
                                        freakshare='com',
                                        filefactory='com',
                                        oron='com',
                                        xerver='co',
                                        mega='co.nz',
                                        uploadable='ch',
                                        hellshare='pl',
                                        fastshare='cz',
                                        junocloud='me',
                                        freshfile='pl',
                                        crocko='com',
                                        oboom='com',
                                        terafile='co',
                                        kingfiles='net',
                                        fileparadox='in',
                                        fileom='com',
                                        billionuploads='com',
                                        sharehost='in',
                                        gigapeta='com',
                                        ryushare='com',
                                        mediafire='com',
                                        ifile='it',
                                        gamefront='com',
                                        load='to',
                                        uploading='com',
                                        hellupload='com',
                                        creafile='net'
                                        )
                    upload_sites.update({'180upload': 'com'})
                    try:
                        dom = dom + '.' + upload_sites[dom]
                        dom = dom.replace('hellshare.pl', 'download.hellshare.pl')
                    except KeyError:
                        self.log.warning(page_url)
                        self.log.warning(str(i) + ': ' + link)
                        continue

                    link = http + '//' + dom + '/' + rest

                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_title=title,
                                         link_url=link)

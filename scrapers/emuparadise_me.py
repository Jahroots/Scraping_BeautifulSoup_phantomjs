# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, ScraperParseException
from sandcrawler.scraper.caching import cacheable


class EmuparadiseMe(SimpleScraperBase):
    BASE_URL = 'https://www.emuparadise.me'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    USER_AGENT_MOBILE = False

    def _fetch_search_url(self, search_term, media_type):
        return u'{base_url}/roms/search.php?section=all&query={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found_results = False
        for searchpath in (
            'div.roms a',
            'div.videos a[href*="/Movies/"]',
            'div.music a[href*="/Movies/"]',
        ):
            for link in soup.select(searchpath):
                # Category link.s
                if link.href.startswith('/roms/roms.php?sysid='):
                    continue
                found_results = True
                self.submit_search_result(
                    link_url=u'{}{}'.format(self.BASE_URL, link.href),
                    link_title=link.text,
                )
        if not found_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        self.log.info('IN PARSE %s', parse_url)
        self._http_session.cookies.set(
            'downloadcaptcha',
            '1',
            domain='www.emuparadise.me'
        )
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    @cacheable()
    def _follow_link(self, link):
        return self.get_redirect_location(
            u'{}{}'.format(self.BASE_URL, link)
        )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.download-link a'):
            if link.href.startswith('//') or link.href.startswith('http'):
                # It's a standalone link - submit it
                href = link.href
                if href.startswith('//'):
                    href = 'http:{}'.format(href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=href,
                    link_title=link.text,
                )
            else:
                url = self.BASE_URL + link.href
                soup = self.get_soup(url)
                if soup.select('#captchadiv'):
                    # LOL - there's a skip captcha link/function.
                    # all it does is set the cookie, which is done in the 'parse'
                    # function.
                    raise ScraperParseException('Found captcha in page.')

                    # self.log.debug('Captcha Found')
                    # # Pull out the noscript version of the iframe.
                    # iframe = None
                    # for noscript in soup.select('noscript'):
                    #     srch = re.search('<iframe src=\"(.*?)\"')
                    #     if srch:
                    #         iframe = srch.group(1)
                    #         break
                    #
                    # solve_soup = self.get(iframe)
                    # image = solve_soup.select_one('img#adcopy-puzzle-image')
                    # response = self.solve_captcha(image['src'])
                    #
                    #
                    #
                    # self.get()
                    #
                    # iframe = soup.find('script', src=re.compile('api-secure.solvemedia.com'))
                    #
                    # key = self.solve_captcha(iframe['src'])
                    #
                    # soup = self.post_soup(
                    #     url, data={'adcopy_response': key,
                    #                                  'adcopy_challenge' : '',
                    #                                  'submit': 'Verify & Download'})
                    # self.save_session_cookies()


                links = soup.select('a[href*="get-download.php"]')
                for link in links:
                    download = self._follow_link(link.href)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=download,
                        link_title=link.text,

                    )



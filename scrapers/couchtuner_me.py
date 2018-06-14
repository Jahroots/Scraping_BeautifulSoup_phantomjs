# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase

class CouchTunerME(ScraperBase):
    BASE_URL = 'https://www.couchtuner.rocks'

    OTHER_URLS = [
        'http://stream2watch.mx',
        'https://www.couchtuner.onl',
        'http://www.couchtuner.onl',
        'http://www.couchtuner.video',
        'http://video247.xyz/',
        'http://watch-series.xyz',
        'http://www.couchtuner.one'
        #http://streamonline.me
    ]
    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # The site's pages seem to be on a different domain
        for url in ():
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _extract_watch_it_here(self, soup):
        wih = soup.find(
            text=re.compile('Watch it here.*', re.IGNORECASE)
        )
        if wih:
            results = soup.select('div.postSDiv a')
            for result in results:
                self.submit_search_result(link_title=result.text, link_url=result.get('href'))

    def _parse_search_results(self, soup):
        if unicode(soup).find(
                u'Nothing Found') >= 0:
            return self.submit_search_no_results()
        links_found = set()
        for post_link in soup.select('div.left-flt a'):
            if post_link['href'] in links_found:
                continue
            links_found.add(post_link['href'])
            post_soup = self.get_soup(post_link['href'])
            # This will either have a 'Watch it here' link, which we submit.
            self._extract_watch_it_here(post_soup)
            # Or an episode list, that links off to pages with a watch it here.
            episode_list = post_soup.find('strong', text='Episode List')
            if episode_list:
                # Grab the content, then all a rel="bookmark" links within.
                for episode_link in post_soup \
                        .find('div', id='content') \
                        .findAll('a', rel='bookmark'):
                    self._extract_watch_it_here(
                        self.get_soup(episode_link['href'])
                    )

        next_button = soup.select('div.nav-previous a')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button[0]['href'])
            )

    def parse(self, parse_url, **extra):
        # XXX
        # On this site we actaully get http://streamonline.me
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for iframe in soup.select('div.postTabs_divs iframe'):
            src = iframe['src']
            if src.find('http') == -1:
                src = 'http:' + src
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=src,
                                     )

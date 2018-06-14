#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase


class CouchTunerEU(ScraperBase):
    BASE_URL =  'http://couch-tuner.ac'
    OTHER_URLS = [
                  'http://icouchtuner.city',
                  'http://icouchtuner.ag',
                  'http://mycouchtuner.ag',
                  'http://mycouchtuner.city',
                  'http://www.couch-tuner.ag',
                  'http://couch-tuner.city',
                  'http://couchtuner.red',
                  'http://www.couchtuner.ag',
                  'http://www.couchtuner.la',
                  'http://couchtuner.city',
                  'http://couchtuner.la',
                  'http://couchtuner.city',
                  'http://couchtuner.eu.com',
                ]

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

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(
            u'<h2>Not Found</h2>') >= 0:
            return self.submit_search_no_results()
        series_links = soup.select('div.post > h2 > a')
        series_urls = [link.get('href') for link in series_links]

        # Open that up, and it's a series of links to episodes.
        for series_soup in self.soup_each(series_urls):
            for episode in series_soup.select('div.entry > ul > li > strong > a'):
                # That link either goes directly to another page, or off
                # to a local page which links to a similar offsite page
                if episode['href'].startswith(self.BASE_URL):
                    # XXX should we follow that? Just submitting for now.
                    # Find the 'Watch it here:&nbsp'; it's next to the link we want.
                    for episode_soup in self.soup_each([episode.get('href')]):
                        wih = episode_soup.find(
                            'span',
                            text=re.compile('Watch it here.*')
                        )
                        if wih:
                            wih_link = wih.find_next()
                            if wih_link.name == 'a':
                                self.submit_search_result(
                                    link_url=wih_link['href'],
                                    link_title=wih_link.text
                                )
                else:
                    self.submit_search_result(
                        link_url=episode['href'],
                        link_title=episode.text
                    )

        next_button = soup.select('div.prev-page a')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button[0]['href'])
            )

    def parse(self, parse_url, **extra):
        # On this site we actaully get http://couchtuner.eu.com/ links
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        # Simple iframes embeds
        for iframe in soup.select('iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe['src'],
            )
        # Also embeds as
        # <div class='postTabs_divs' id='postTabs_1_103780'>
        # <span class='postTabs_titles'><b>Vidup</b></span><b id='ko' data-iframe='
        # <iframe width="540" height="330" src="http://vidup.me/embed-w4dpx7lei7t4.html" frameborder="0" allowfullscreen></iframe>
        # '></b></div>

        # unsure if 'b' will remain - so fetch the parent, the iterate looking for
        # 'data-iframe' in each element.

        for container in soup.select('div.postTabs_divs'):
            for element in container.children:
                try:
                    dataiframe = element['data-iframe']
                except (KeyError, TypeError):
                    pass
                else:
                    for iframe in self.make_soup(dataiframe).select('iframe'):
                        self.submit_parse_result(
                            index_page_title=self.util.get_page_title(soup),
                            link_url=iframe['src'],
                        )



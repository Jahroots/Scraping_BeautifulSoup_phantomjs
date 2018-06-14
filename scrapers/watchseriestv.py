from base64 import decodestring

from sandcrawler.scraper import ScraperBase


class WatchSeries(ScraperBase):
    BASE_URL = 'http://onwatchseries.to'
    OTHER_URLS = [
        'http://thewatchseriestv.to/',
        'http://watchseriestv.to/',
        'http://watchseries.to/',
        'http://watch-series-tv.to/',
        'http://thewatchseries.to/',
        'http://thewatchseries.to',
        'http://watchseriesonline.in',
        'http://watchseriesonline.eu'
    ]

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    # Could also be this...
    # _base_url = 'http://watchseries.to/'

    def setup(self):

        raise NotImplementedError('Duplicate scraper - use the_watch_series.py')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        # XXX quote -> url encode
        base_search_url = self.util.canonicalise(
            self.BASE_URL,
            'search/' + self.util.quote(search_term)
        )
        self._discovered_urls = set()
        self._parse_search_page(base_search_url)

    def _parse_search_page(self, url):
        """
        The pagination on this site is bung.  Really.
        Keep a list of urls we've found, and when they start
        duplicating, we've started looping pages :|

        BUT, as a kicker, once we have one repeat, there are still new
         entries afterward.  BOO HISS.

        So keep going until we have a full page of repeats.

        """
        soup = self.get_soup(url)
        # Make sure we have any results.
        if soup.text.find(
                'Sorry we do not have any results for that search.'
        ) >= 0:
            # Less than one page of results means you get a 'next' link,
            # but the following page has a 'no results found'
            # If we've found any items, just finish; otherwise alert the
            # fact no results were found.
            if not self._discovered_urls:
                self.submit_search_no_results(url=url)
            return
        # dig out the strong tag in <a><strong>NAME</strong></a>
        # then get the info from the a (parent)
        titles = soup.select('div > div > div > a > strong')
        any_hits = False
        for title in titles:
            link = title.parent.get('href')
            lookup_key = (title.text, link)
            if lookup_key in self._discovered_urls:
                self.log.debug('Entry %s already discovered.  Skipping.',
                               lookup_key)
                continue
            any_hits = True
            self._discovered_urls.add(lookup_key)
            self._expand_search_page(link)
        if not any_hits:
            self.log.debug('Full page of duplicates - finishing.')
            return

        # Now check or a 'next' lnk and follow it if present.
        next_link = soup.find('a', text='Next Page')
        if next_link:
            self.log.debug('---------------- Found next page: %s ----------------', next_link)
            self._parse_search_page(
                self.util.canonicalise(self.BASE_URL, next_link.get('href')))

    def _expand_search_page(self, link):
        for soup in self.soup_each([self.util.canonicalise(self.BASE_URL, link)]):
            for season_block in soup.findAll('div', {'itemprop': 'season'}):
                season = self.util.find_numeric(
                    season_block.find('span', {'itemprop': 'name'}).text)
                for episode_block in season_block.select('li'):
                    episode = episode_block.find(
                        'meta', {'itemprop': 'episodenumber'})['content']
                    link = episode_block.find('a')
                    title = link.find('span').text
                    self.submit_search_result(
                        link_title=soup.title.text + " " + title,
                        link_url=self.util.canonicalise(
                            self.BASE_URL, link['href']),
                        series_season=season,
                        series_episode=episode,
                    )

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        for row in soup.select('table#myTable tr'):
            if 'download_link_sponsored' in row['class']:
                # Skip sponsored links (thanks, css!)
                continue
            # Grab our link, follow it and find the push_button button in the
            # middle of the new page.
            link = row.find('a', 'buttonlink')
            url = decodestring(link.href.split('/cale.html?r=')[1])
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     )

            # for link_soup in self.soup_each([self.util.canonicalise(self._base_url, link['href'])]):
            #     button = link_soup.select_one('a.push_button.blue')
            #     if button:
            #         self.submit_parse_result(index_page_title=soup.title.text.strip(),
            #                                  link_url=button['href'],
            #                                  )



# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Dl4All(SimpleScraperBase):
    BASE_URL = 'http://www.dl4all.ws'

    OTHER_URLS = ['http://dl4all.ws', ]
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)



    def search(self, search_term, media_type, **extra):
        srch_res = self.get_soup(
            self.BASE_URL + '/016/tag/{}.html'.format(search_term))

        self._parse_search_results(srch_res)

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.category a h1'):
            found = True
            link = link.parent
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)
        if not found: self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.category h1')
        series_season = None
        series_episode = None
        index_page_title = self.util.get_page_title(soup)
        if title:
            title = title.text.strip()
            series_season, series_episode = self.util.extract_season_episode(title)

        # There are two quote blocks - the first one is a generic header with a
        # whole bunch of (massively populated) pastebin links.
        # This isn't on every page... >.>
        # So let's skip pastebin links.
        # There's also non ahref'd links.

        submitted = set()
        for quotebox in soup.select('.quote'):
            for link in quotebox.select('a'):
                if 'pastebin' not in link['href']:
                    submitted.add(link['href'])
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link['href'],
                        link_text=link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            for link in self.util.find_urls_in_text(unicode(quotebox)):
                if link not in submitted and 'pastebin' not in link:
                    submitted.add(link)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Movie1k(SimpleScraperBase):
    BASE_URL = 'http://www.movie1k.pw'
    OTHER_URLS = ['http://www.movie1k.im', 'http://www.moviez1k.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'Sorry, we couldn\'t find any results based on your search query.'

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/page/{page}/?s={search_term}'.format(base_url=self.BASE_URL,
                                                                                     search_term=search_term,
                                                                                     page=page)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('.entry-title a'):
            self.submit_search_result(link_url=link['href'],
                                      link_title=link.text
                                      )

    def _parse_parse_page(self, soup):

        title = soup.select_one('.entry-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.easy-table.easy-table-default a') + soup.select('.entry-content.clearfix p a'):
            href = link.href

            if not href.startswith(self.BASE_URL):

                if link.href.startswith('http://www.linkembed.net/watch.php?idl='):
                    href = self.util.unquote(link.href[39:])
                elif link.href.startswith('http://www.linkembed.net/watche.php?idl='):
                    href = base64.decodestring(link.href[40:])

                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode
                                         )
        for links in soup.select('div#content a'):
            if 'http://www.movie1k.pw/watch.html?url=' in links.href:
                link = links.href.split('url=')[-1]
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode
                                         )



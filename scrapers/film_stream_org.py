# coding=utf-8

import re

from bs4 import NavigableString

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmStreamOrg(SimpleScraperBase):
    BASE_URL = 'http://film-stream.biz'

    OTHER_URLS = [
        'http://film-stream.info',
        'http://film-stream.cc',
        'http://film-stream.org'
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ita"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'No posts found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.galleryitem h3 a'):
            try:
                img = result.parent.parent.find('img')
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text,
                    image=img['src'],
                )
            except Exception as e:
                self.log.exception(e)

    def find_season_episode_timessymbol(self, text):
        # Matches "XxY" with html times symbol
        if not text:
            return (None, None)
        # print text
        m = re.search(u'(\d+)×(\d+)', text, re.UNICODE)
        if m:
            series, episode = m.groups()
            return int(series), int(episode)
        return (None, None)

    def _parse_parse_page(self, soup):
        title = soup.select_one('.postcontent h2').text
        # Grab extrernal links in the content

        # Series are
        # Generally layed out like so
        # 2x03 Episode Name - Link1 - Link 2 - Link 3
        # Keep a contextual season/episode; check the previous text for
        # each link to see if we're on a new episode.
        # Clear this if we're within a table.
        (season, episode) = (None, None)
        for link in soup.select('div.postcontent a'):
            # Skip wikipedia/imdb/local/ad lnks
            skip = False
            for skip_flag in ('film-stream.info', 'film-stream.cc', 'wikipedia', 'imdb', 'xviralex', 'freetimefoto', 'aznotizie.com'):
                if link['href'].find(skip_flag) >= 0:
                    skip = True
                    break
            if skip:
                continue
            if link.parent.name == 'td' or link.parent.parent.name == 'td':
                (season, episode) = (None, None)
            else:
                # The season/epsiode may be included here.
                (this_season, this_episode) = self.find_season_episode_timessymbol(link.text)
                if this_season and this_episode:
                    (season, episode) = (this_season, this_episode)
                else:
                    # Check the text before me.
                    prev = link.previous
                    if type(prev) is NavigableString:
                        (this_season, this_episode) = self.find_season_episode_timessymbol(
                            link.previous)
                        if this_season and this_episode:
                            (season, episode) = (this_season, this_episode)

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

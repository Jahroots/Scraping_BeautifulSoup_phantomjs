# -*- coding: utf-8 -*-
import re

import jsbeautifier

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class HappyStreams(SimpleScraperBase):
    BASE_URL = 'http://happystreams.net'
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        raise NotImplementedError

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?op=search&k=' + search_term

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='Next »')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('.link b'):
            self.submit_search_result(
                link_url=result.parent['href'],
                link_title=result.text
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.title.text.replace('Watch ', '').strip()
        season, episode = self.util.extract_season_episode(title)

        page2 = self.post(self.BASE_URL + '/dl', data={
            'op': 'download1', 'usr_login': '', 'id': soup.find('input', dict(name='id'))['value'],
            'fname': soup.find('input', dict(name='fname'))['value'],
            'referer': '', 'hash': soup.find('input', dict(name='hash'))['value'],
            'imhuman': 'Proceed to video'

        }).text

        paccked_search = re.search(
            "<script type='text/javascript'>(eval.*?)</script>",
            page2,
            re.DOTALL
        )
        if not paccked_search:
            self.log.error('Could not extract chunk from page.')
            return

        paccked = paccked_search.group(1)

        if paccked:
            pcontent = jsbeautifier.beautify(
                paccked.replace('"', '\''))  # jsunpack.unpack(paccked[0].replace('"','\''))
            vidlinksearch = re.search("file:\s*'(.+?)'", pcontent)
            if not vidlinksearch:
                raise ValueError("Could not extract video link")
            vidlink = vidlinksearch.group(1)


            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=vidlink,
                link_title=title,
                series_season=season,
                series_episode=episode
            )

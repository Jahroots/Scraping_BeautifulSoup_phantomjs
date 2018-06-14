#coding=utf-8

import random
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class IceFilmsInfo(SimpleScraperBase):

    BASE_URL = 'http://www.icefilms.info'
    LONG_SEARCH_RESULT_KEYWORD = '2015'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('TODO Issue with cookie auth.')
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.long_parse = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?q=' + \
            self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'No results found for'

    def _fetch_next_button(self, soup):
        # no apparent pagination.
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.title a'):
            # Follow it - do we have season list?  Yes? Then submit htem.
            link_soup = self.get_soup(self.BASE_URL + result['href'])
            links = link_soup.select('span.list a')
            if links:
                for link in links:
                    if 'href' in link.attrs and link['href'] != '#':
                        season, episode = \
                            self.util.extract_season_episode(link.text)
                        self.submit_search_result(
                            link_url=self.BASE_URL+link['href'],
                            link_title=result.text + " " + link.text,
                            series_season=season,
                            series_episode=episode,
                        )
            else:
                # Otherwise it's this page.
                self.submit_search_result(
                    link_url=self.BASE_URL+result['href'],
                    link_title=result.text
                )


    def parse(self, parse_url, **extra):

        # Suck the id out of the URL and go find our iframe
        idsearch = re.search('v=(\d+)', parse_url)

        if idsearch:
            vid_id = idsearch.group(1)
            # Grab the iframe.
            iframe_url = self.BASE_URL + \
                '/membersonly/components/com_iceplayer/video.php?vid=' + \
                vid_id
            iframe_soup = self.get_soup(iframe_url)
            data = {'id': None,
                    's': 10383,
                    'iqs': '',
                    'url':'',
                    'm': 10270,
                    'cap': '',
                    'sec': '37fn8Oklq',
                    't': vid_id}
            for link in iframe_soup.select('div#srclist a'):
                # Reach out to their handler.
                src_idsearch = re.search('go\((\d+)\)', link.attrs['onclick'])

                if src_idsearch:
                    data['id'] = src_idsearch.group(1)
                    response = self.post(
                        self.BASE_URL +
                        '/membersonly/components/com_iceplayer/video.phpAjaxResp.php?s={}&t{}'.format(data['id'],data['t']),
                        data=data
                    )
                    self.log.debug(response.text)
                    hop_soup = self.get_soup(self.BASE_URL + response.text)
                    # Find the last link on that page.
                    link_url = hop_soup.select('a')[-1]['href']
                    self.submit_parse_result(index_page_title=hop_soup.title.text.strip(),
                                             link_url=link_url
                                             )



# -*- coding: utf-8 -*-
import random
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import time


class RlsBBCom(SimpleScraperBase):
    BASE_URL = 'http://rlsbb.ru'
    SEARCH_URL = 'http://search.rlsbb.ru'

    OTHER_URLS = ['http://old.rlsbb.com','http://rlsbb.com', SEARCH_URL, BASE_URL, ]
    SINGLE_RESULTS_PAGE = True


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)


        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)


    def _get_page_url(self, search_term, page=1):
        return self.SEARCH_URL + '/lib/search526049.php?phrase=%s&pindex=%s&rand=%s' % (
            self.util.quote(search_term),
            page,
            random.random(),
        )

    def search(self, search_term, media_type, **extra):
        url =self._get_page_url(search_term)
        resp = self.get(url)
        json_data = json.loads(resp.content.replace('\xef\xbb\xbf', ''))
        if 'results' not in json_data \
                or not json_data['results']:
            return self.submit_search_no_results()
        if type(json_data['results'])==int:
            time.sleep(json_data['results']+1)
            resp = self.get(url)
            json_data = json.loads(resp.content.replace('\xef\xbb\xbf', ''))
            if 'results' not in json_data or not json_data['results']:
                return self.submit_search_no_results()

        page = 1
        while True:
            if self._parse_search_result(json_data):
                page += 1
                url = self._get_page_url(search_term, page)
                resp = self.get(url)
                json_data = json.loads(resp.content.replace('\xef\xbb\xbf', ''))
            else:
                break


    def _parse_search_result(self, json_data):
            if type(json_data['results'])==int:
                return False
            else:
                for result in json_data['results']:
                    self.submit_search_result(
                        link_url='http://%s/%s' % (result['domain'],result['post_name']),
                        link_title=result['post_title']
                    )
                return len(json_data['results']) >= 10

    def _parse_parse_page(self, soup):
        season, episode = self.util.extract_season_episode(soup.select_one(".postTitle").text)

        dload_links = soup.select('.postContent a')
        for link in dload_links:
            if link.text not in ('iMDB', 'Torrent Search', 'HOMEPAGE', 'NFO', 'STEAM', 'Homepage'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=link['href'],
                                         series_season=season,
                                         series_episode=episode
                                         )

        # search in users' comments
        user_posted_links = soup.select('.messageBox .content a')
        for link in user_posted_links:
            self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=link['href'],
                                     series_season=season,
                                     series_episode=episode
                                     )

class OldRlsbbCom(RlsBBCom):
    BASE_URL = 'http://old.rlsbb.com'
    SEARCH_URL = 'http://search.rlsbb.com'



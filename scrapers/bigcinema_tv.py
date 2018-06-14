# coding=utf-8

import re
from sandcrawler.scraper import SimpleScraperBase, ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import VideoCaptureMixin
import json


class BigCinemaTV(SimpleScraperBase, VideoCaptureMixin):
    BASE_URL = 'http://bigcinema.cc'
    OTHER_URLS = ['https://bigcinema.to', 'http://bigcinema.to', 'http://bigcinema.tv']

    LONG_SEARCH_RESULT_KEYWORD = u'Воронины'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self._request_connect_timeout = 300
        self._request_response_timeout = 300

        # self.requires_webdriver = ('parse',)
        # self.webdriver_type = 'phantomjs'  # - cannot use due to usage of extract_network_logs()
        #self.adblock_enabled = True

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'следующая')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _fetch_no_results_text(self):
        return u"Удивительно, но поиск не дал результатов"

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + u'/search/topics?q=' + search_term.decode('utf-8')

    # def search(self, search_term, media_type, **extra):
    #     search_url = self.BASE_URL + u'/search/topics?q=' + search_term.decode('utf-8')
    #     for soup in self.soup_each([search_url, ]):
    #         self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        if unicode(soup).find(
                u'Извините, ничего не найдено') >= 0:
            return self.submit_search_no_results()
        for topic in soup.select('div.topic'):
            link = topic.select('a.watch')
            if not link:
                continue
            link = link[0]['href']
            if link.endswith('noindex'):
                continue
            title = topic.select('h2.title')[0].text
            self.submit_search_result(
                link_url=link,
                link_title=title
            )

    def use_embed_element(self):
        return False

    def _video_player_ids(self):
        return []

    def _video_player_classes(self):
        return ['buzz-container', ]

    def decode_uppod(self, file_code):
            file_code = file_code[1:]
            uni_file_code = ''
            for i in range(0, len(file_code), 3):
                uni_file_code += '%u0' + file_code[i:i + 3]
            decoded_url =re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), uni_file_code)
            return decoded_url


    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        players = soup.select('div.player_container')
        if players:
            for player in players:
                script_text = player.find('script', text=re.compile("file5")).text
                result = re.search("""filejs:\s?[\"|\'](.*)[\"|\']""", script_text)
                soup = self.get(result.group(1))
                data = json.loads(soup.text)
                for a in data:
                    for b in a['folder']:
                        urls = re.sub('\[\d+\]', '', b['file']).split('and')

                        for url in urls:
                            or_l = url.split('or')
                            for l in or_l:
                                self.submit_parse_result(
                                    index_page_title=index_page_title,
                                    link_url=l.strip(),
                                    link_title=b['title'],
                                    series_season=series_season,
                                    series_episode=series_episode,
                                )




    # def parse(self, page_url, **extra):
    #     # XX playlists are embedded and encrpted.
    #     urls = self._capture_video_urls(page_url)
    #     title = self.util.get_page_title(self.get_soup(page_url))
    #     # found = False
    #     for url in urls:
    #         self.submit_parse_result(index_page_title=title,
    #                                  link_url=url)
            # found = True
        # if not found:
        #     raise ScraperParseException('Did not find any results on %s',
        #                                 page_url)

            # soup = self.get_soup(page_url)
            # containers = soup.select('div.player_container div')
            # self.found_ids = []
            # for container in containers:
            #     c_id = container.get('id')
            #     if c_id and c_id != 'player_trailer':
            #         self.found_ids.append(c_id)
            # if self.found_ids:

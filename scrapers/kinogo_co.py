#coding=utf-8

import base64
import re
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import UppodDecoderMixin


class KinogoCo(OpenSearchMixin, SimpleScraperBase,  UppodDecoderMixin):

    BASE_URL = 'http://kinogo.cc'
    OTHER_URLS = ['http://kinogo.club/','http://kinogo.co',]
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SEARCH_TERM =''
    PAGE = 1
    COUNT = 0
    TRELLO_ID = 'udY9RlC0'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = ('parse', )

        self.search_term_encoding = 'windows-1251'

    def _fetch_no_results_text(self):
        return u"К сожалению, поиск по сайту не дал никаких результатов."

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        if soup.select_one('#nextlink'):
            soup = self.post_soup(self.BASE_URL + '/index.php?do=search', data={'titleonly': 3,
                                                   'do': 'search',
                                                   'subaction': 'search',
                                                   'search_start' : self.PAGE,
                                                   'full_search' : 0,
                                                   'result_from' : self.COUNT,
                                                   'story': self.SEARCH_TERM})

            return soup
        return None

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        self.PAGE = 1
        self.COUNT = 0

        soup = self.post_soup(self.BASE_URL, data = { 'titleonly' : 3,
                                                    'do' : 'search',
                                                    'subaction' : 'search',
                                                    'story': search_term})

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.shortstory'):
            link = result.select('div.shortstorytitle h2 a')[0]
            image = None
            img = result.select('div.shortimg img')
            if img:
                image = img[0]['src']
            self.COUNT += 1
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image,
            )

        if self.COUNT == 0:
            return self.submit_search_no_results()

        soup = self._fetch_next_button(soup)
     
        if soup and self.can_fetch_next():
            self._parse_search_result_page(soup)

    def _video_player_classes(self):
        return ('uppod_style_video', 'section')

    def _video_player_ids(self):
        return ( )

    def _packet_matches_playlist(self, packet):
        return False

    def decodeuppod(self, data, ch1, ch2):
        if data[:-1].endswith(ch1) and data[2] == ch2:
            srev = data[::-1]
            try:
                loc3 = int(float(srev[-2:]) / 2)
            except ValueError:
                return data
            srev = srev[2:-3]
            if loc3 < len(srev):
                i = loc3
                while i < len(srev):
                    srev = srev[:i] + srev[i + 1:]
                    i += loc3
            data = srev + "!"
        return data

    def decodeuppodtexthash(self, data):
        hash = "0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"
        data = self.decodeuppod(data, "r", "A")
        data = data.replace("\n", "")
        hash = hash.split('ih')

        if data.endswith('!'):
            data = data[:-1]
            taba = hash[3]
            tabb = hash[2]
        else:
            taba = hash[1]
            tabb = hash[0]

        i = 0
        while i < len(taba):
            data = data.replace(tabb[i], "__")
            data = data.replace(taba[i], tabb[i])
            data = data.replace("__", taba[i])
            i += 1

        result = base64.b64decode(data)
        return result

    def parse(self, parse_url, **extra):

        try:
            soup = self.get_soup(parse_url)

            try:
                url= soup.select_one('div[class="box visible"]').text.split('file:')[1].split('}')[0].replace('"','').strip()
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url)
                return
            except Exception as e:
                self.log.warning('The item should be uppod' + str(e))

            try:
                encoded_text = soup.select_one('div.section script').text
                decoded_text = re.search("decode\(\'(.*)\'\)\);", encoded_text)
                if decoded_text:
                    decoded_text = base64.b64decode(decoded_text.group(1))
                file_links = self.make_soup(decoded_text).select_one('param[name="flashvars"]')['value'].split('file=')[-1].split('&')[0]
                decoded_url = self.decodeuppodtexthash(file_links)
                if 'txt' not in decoded_url:
                    self.submit_parse_result (index_page_title = self.get_soup(parse_url).title.text.strip(),
                                             link_url = decoded_url
                                             )
            except Exception as e:
                self.log.warning(str(e))

        except Exception as ex:
            self.log.warning(str(ex))

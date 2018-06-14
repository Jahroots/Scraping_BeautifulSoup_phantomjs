# coding=utf-8
import json
from base64 import decodestring

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


def DecodeUppodText(data):
    # print data
    a = (
        "G", "d", "R", "0", "M", "Y", "4", "v", "6", "u", "t", "i", "f", "c", "s", "l", "B", "5", "n", "2", "V", "Z",
        "J", "m", "L", "=")
    b = (
        "1", "w", "Q", "o", "9", "U", "a", "N", "x", "D", "X", "7", "z", "H", "y", "3", "e", "g", "T", "W", "b", "8",
        "k", "I", "p", "r")
    for i in xrange(len(a)):
        data = data.replace(b[i], "__")
        data = data.replace(a[i], b[i])
        data = data.replace("__", a[i])
    # print data
    return json.loads(decodestring(data))


class OnlineStepashkaCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://online.stepashka.com'

    LONG_SEARCH_RESULT_KEYWORD = 'The Hateful 8'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        # self.requires_webdriver = ('parse',)

    def _fetch_no_results_text(self):
        return u"К сожалению, поиск по сайту"

    def _fetch_search_url(self, search_term):
        return self.BASE_URL + '/'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.shortstory'):
            link = result.select('div.video-title a')[0]
            asset_type = None
            if link['href'].find('/filmy/') >= 0:
                asset_type = ScraperBase.MEDIA_TYPE_FILM
            elif link['href'].find('/serialy/') >= 0:
                asset_type = ScraperBase.MEDIA_TYPE_TV

            image = result.find('img', 'cover')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image['src'],
                asset_type=asset_type,
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('.titleHone').text + ' | ' + soup.select_one('.alternative-title').text

        try:
            url2decode = str(soup).split(' value="st=')[1].split('"')[0]
        except IndexError as e:
            self.log.warning(e)
            return

        player_data = DecodeUppodText(self.get(url2decode).text)
        # pprint(player_data)

        if 'file' in player_data:
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=player_data['file'],
                link_title=title)
        else:
            player_data = eval(player_data['pl'])['playlist']
            for lst in player_data:
                for episode in lst['playlist']:
                    # {
                    #     'comment': '17 Серия  (Сезон 4)',
                    #     'pltitle': '4-17',
                    #     'file': 'http://ppp2.pirateplayer.com/video/f8c380f42985f317f88819ccf7fd17c6/mp4/s/Dve.razorivshiesya.devochki/s04e17.mp4',
                    #     'thumbs': 'http://online.stepashka.com/player/3/pwVKeWnbXo_TVcKSh57D-XcMHHo-DJ20d/f8c380f42985f317f88819ccf7fd17c6',
                    #     'thumbs_size': '10x10'
                    # },
                    series_season, series_episode = self.util.extract_season_episode(episode['file'].split('/')[-1])

                    self.submit_parse_result(
                        index_page_title=soup.title.text.strip(),
                        link_url=episode['file'],
                        link_title=title + ' ~ ' + episode['comment'].decode('utf8'),
                        series_season=series_season,
                        series_episode=series_episode,
                    )

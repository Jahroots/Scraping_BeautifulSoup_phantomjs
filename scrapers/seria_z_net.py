# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import VideoCaptureMixin, SimpleScraperBase
import re
import json



class SeriaZNet(SimpleScraperBase, VideoCaptureMixin):
    BASE_URL = 'http://seria-z.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'
        # self.requires_webdriver = ('parse',)

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)



    def _fetch_no_results_text(self):
        return u'Ничего не найдено'

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/island/{}?keyword={}'.format(start, search_term)

    def _fetch_next_button(self, soup):
        link = None
        try:
            link = soup.find('a', text=u'»')['href']
        except TypeError:
            pass
        return link if link else None


    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.find_all('a', itemprop='url'):
            self.submit_search_result(
                link_title=link['title'],
                link_url=link.href
            )


    def _video_player_ids(self):
        return ('playerarea',)

    def _video_player_classes(self):
        return ()

    def _get_playlist(self, packet):
        return None

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        index_page_title = self.util.get_page_title(soup)
        script_text = soup.select_one('div.leftside script').text
        hash_text = re.search("""hash = \'(.*)\'; globals.player_type""", script_text)
        if hash_text:
            hash_text = hash_text.group(1)
        season_id = re.search("""season_id = \'(.*)\'; globals.hash""", script_text)
        if season_id:
            season_id = season_id.group(1)
        play_list_soup = json.loads(self.get_soup('http://seria-z.net/upp/player/{}/{}/plfl.txt'.format(hash_text, season_id)).text)
        play_list = play_list_soup['playlist']
        for url in play_list:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_title=url['comment'],
                link_url=url['file'],
            )
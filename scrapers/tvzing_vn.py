# -*- coding: utf-8 -*-
import lxml.objectify
from Crypto.Cipher import AES
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TvZingVn(SimpleScraperBase):
    BASE_URL = 'https://tv.zing.vn'
    decrypt_key = 'f_pk_ZingTV_1_@z'
    OTHERS_URLS = ['http://tv.zing.vn/']

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'Elephant'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'vie'
        self.requires_webdriver = True
        # self.webdriver_type = 'phantomjs'
        self.adblock_enabled = False
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    # @staticmethod
    # def decrypt(ciphertext, key):
    #     iv = ciphertext[:AES.block_size]
    #     cipher = AES.new(key, AES.MODE_CBC, iv)
    #     plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    #     return plaintext.rstrip(b"\0")

    def search(self, search_term, media_type, **extra):
        self.log.debug("media_type: " + media_type)
        SEARCH_URL_BY_MEDIA_TYPE = {self.MEDIA_TYPE_FILM: 'movie',
                                    self.MEDIA_TYPE_TV: 'program'}
        self.search_url = self.BASE_URL + '/tim-kiem/' + '/index.html'
        search_url = self.search_url + '?q=' + search_term
        for soup in self.soup_each([search_url, ]):
            # self.show_in_browser(soup)
            self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'Có 0 kết quả tìm kiếm'

    def _fetch_next_button(self, soup):
        curr_page = soup.select_one('.pagination.txtCenter.pdright10.pdtop20 li a.active')
        if curr_page:
            next_page = curr_page.parent.findNextSibling('li')
            return soup._url.split('?')[0] + next_page.a.href if next_page else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.item'):
            self.submit_search_result(
                link_url=self.BASE_URL + result.find('a')['href'],
                link_title=result.find('a').text
            )

    def _parse_parse_page(self, soup):
        self.webdriver()
        self.webdriver().set_page_load_timeout(30)
        try:
            self.webdriver().get(soup._url)
        except TimeoutException:
            pass
        soup = self.make_soup(self.webdriver().page_source)
        box_player = soup.select_one('div.box-player')
        if box_player:
            series_season = series_episode = None
            title = soup.select_one('h1')
            if title and title.text:
                series_season, series_episode = self.util.extract_season_episode(title.text)
            script_text = soup.text
            com = re.compile("|".join(x for x in ['source: \"(.*)\",', 'video\d+ = \"(.*)\";']))
            all_links = com.findall(script_text)
            for link in all_links:
                if link[0] or link[1]:
                    link = filter(None, link)[0]
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_title=link,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
        online_link = soup.select_one('a[class="btn-default btn-green"]')
        if online_link:
            try:
                self.webdriver().get(self.BASE_URL + online_link['href'])
            except TimeoutException:
                pass
            online_soup = self.make_soup(self.webdriver().page_source)
            series_season = series_episode = None
            title = online_soup.select_one('h1')
            if title and title.text:
                series_season, series_episode = self.util.extract_season_episode(title.text)
            script_text = online_soup.text
            com = re.compile("|".join(x for x in ['source: \"(.*)\",', 'video\d+ = \"(.*)\";']))
            all_links = com.findall(script_text)
            for link in all_links:
                if link[0] or link[1]:
                    link = filter(None, link)[0]
                    if 'http:' not in link:
                        link = 'http:'+link
                    self.submit_parse_result(index_page_title=online_soup.title.text.strip(),
                                             link_url=link,
                                             link_title=link,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
        series = soup.select('.subtray.flex-des')
        if series:
            for item in series:
                try:
                    self.webdriver().get(self.BASE_URL + item.select_one('.item.cur-p').a['href'])
                except TimeoutException:
                    pass
                ep_soup = self.make_soup(self.webdriver().page_source)
                series_season = series_episode = None
                title = ep_soup.select_one('h1')
                if title and title.text:
                    series_season, series_episode = self.util.extract_season_episode(title.text)
                script_text = ep_soup.text
                com = re.compile("|".join(x for x in ['source: \"(.*)\",', 'video\d+ = \"(.*)\";']))
                all_links = com.findall(script_text)
                for link in all_links:
                    if link[0] or link[1]:
                        link = filter(None, link)[0]
                        self.submit_parse_result(index_page_title=ep_soup.title.text.strip(),
                                                 link_url=link,
                                                 link_title=link,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )
        self.webdriver().close()
        self.webdriver().quit()

#         def process_page(url_, series_episode=None):
#
#             try:
#                 video_player_page = self.get(url_).content
#
#                 idx = video_player_page.find('xmlURL: "')
#                 if idx == -1:
#                     return  # no link to download/view
#                 url2 = video_player_page[idx + 9:idx + 200].split('\n')[0][:-3]
#
#                 obj = lxml.objectify.fromstring(self.get(url2).text)
#             except:
#                 # from pprint import pprint
#                 # pprint(locals())
#                 raise
#
#             for stream_type in ("f240", "f360", "source", "f480", "f720", "f1080"):
#                 try:
#                     self.submit_parse_result(index_page_title=soup.title.text.strip(),
#                                              link_url=(AES.new(self.decrypt_key, AES.MODE_CBC, self.decrypt_key)
#                                                        .decrypt(str(obj.item.find(stream_type)).decode('hex')).rstrip(
#                                                  b"\0")
#                                                        .replace('htmm://', 'http://')
#                                                        if not str(obj.item.source).startswith('http')
#                                                        else obj.item.source),
#                                              link_title=obj.item.title,
#                                              series_season=obj.item.title,
#                                              series_episode=obj.item.performer)
#                 except:
#                     pass
#
#         series = soup.select('.subtray.flex-des')
#         if series:
#             for item in series:
#                 process_page(self.BASE_URL + item.select_one('.item.cur-p').a['href'])
#
#         else:  # single-serie video
#             if u'Nội dung tạm thời bị đóng theo yêu cầu của bên sở hữu bản quyền' not in unicode(soup):
#                 if soup.select_one('.button-list a') and not "xmlURL: " in unicode(soup):
#                     url = self.BASE_URL + soup.select_one('.button-list a')['href']
#                     process_page(url)
#
#
#
#
#
# if __name__ == '__main__':
#     enc = '7804dd8e311e4eaa7b6cc279a7b41795f9aa1e9cf1dfe3491a8d1aaca126c9f9a1a9bf8b689f0529746a7ad7e2bb0569c6c61dd7cb065464c519381e85c38eaaa56504fc0a1011009e7484d8290b3ca798999c2c8ee2b7160e87d5e3ab3b32062a9a3cdbd85a6e28f11ba377156ce0184b639b07dc71fa8ec91a31e1d6c20cd80ca68d98ec336179dd17b95cf2af71d0a723ee894ffabb62e81e348861b02ced'
#     enc = '28560473f4a916d34ab66d2da52d2c80719a0d4123b3eaa800eb7b328c4cc6b4d33014c57b469975bb270628a3f1c11975d89bacf11e5efb532208802285117760034e516f19feff6ee4c14cb46905bc106c9647324bdc5dbdde94bddf87eef15ac468f78021ebefbab8cc252ed08bc16036ff57178028c396f318e76867f86986ba9198104c01f2ec1c829b70441c9b6ba78fc2fc19a6fbd63bc9af1a784b1f9ae1eb85aaa0bc4b7d21599d11aa18f7'
#     ########################
#     key = 'f_pk_ZingTV_1_@z'
#
#
#     ##############################
#     def decrypt(ciphertext, key):
#         # cipher = AES.new(key, AES.MODE_CBC, key)
#         return AES.new(key, AES.MODE_CBC, key).decrypt(enc.decode('hex'))


    # print AES.new(key, AES.MODE_CBC, key).decrypt(enc.decode('hex')).replace('htmm://', 'http://')
    #
    # print '\n', decrypt(enc.decode('hex'), key)

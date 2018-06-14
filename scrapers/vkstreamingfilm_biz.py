# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin
import re
import base64

class VkstreamingfilmBiz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.voirfilm.sc'
    OTHERS_URLS = ['http://www.filmstreamingvk.co', 'http://www.vkstreamingfilm.org', 'http://www.vkstreamingfilm.co', 'http://www.vkstreamingfilm.biz']
    TRELLO_ID = '7lKtU871'
    LONG_SEARCH_RESULT_KEYWORD = '2016'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(VkstreamingfilmBiz, self).get(url, allowed_errors_codes=[403, ], **kwargs)


    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.mov a[class="mov-t nowrap"]'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )
            found=1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        script_text = soup.find('script', text=re.compile('var _a ='))

        data = re.search("var _a = \[.+", script_text.text).group(0)
        data = data.split("['")[1].split("'];")[0]
        data = 'http://' + base64.decodestring(data).split('\xc8\xbe\x8c\x1d\xcd\x11\x1d\xaf')[1]



        title = soup.select_one('h1').text.strip()
        self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=data,
                link_title=title,
            )
        for link in soup.select('div.fstory-video-block iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title,
            )


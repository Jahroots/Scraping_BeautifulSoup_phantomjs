# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import VideoCaptureMixin


class PPTVCom(SimpleScraperBase):
    BASE_URL = 'http://www.pptv.com'
    OTHER_URLS = 'http://www.pptv.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "zho"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in (self.BASE_URL, 'http://www.pptv.com', 'http://v.pptv.com'):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.proxy_region = 'ch'

    def _fetch_no_results_text(self):
        return u'很抱歉，没有找到相关搜索结果'

    def _fetch_search_url(self, search_term, media_type):
        return 'http://search.pptv.com/s_video?kw=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        for link in soup.select('div.page a.pg'):
            if 'title' in link.attrs and link['title'] == u'下一页':
                return link['href']
        return None

    def __handle_result(self, result, soup):
        if result['href'].startswith('http://v.pptv.com'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )
        elif result['href'].startswith('http'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     parse_url=result['href'],
                                     link_url=result['href'],
                                     link_title=result['title'],
                                     image=self.util.find_image_src_or_none(result, 'img')
                                     )

    def _parse_search_result_page(self, soup):
        has_main_entries = False
        for result in soup.select('div#search-result div.scon div.bpic a'):
            has_main_entries = True
            self.__handle_result(result, soup)
        if not has_main_entries:
            for result in soup.select('div.ui-resp-pics ul.cf li > a'):
                self.__handle_result(result, soup)

    def _video_player_classes(self):
        return ()

    def _video_player_ids(self):
        return ('pptv_playpage_box',)

    def _packet_matches_playlist(self, packet):
        return False

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.title.text.strip()
        title = soup.select_one('.hd h3')
        if title and title.text:
            title = title.text

        # for url in self._capture_video_urls(parse_url):
        #     if url.startswith('http'):
        #         self.submit_parse_result(
        #             index_page_title=index_page_title,
        #             link_url=url
        #         )

        for link in soup.select('.view.j_videoPlay a'):
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_title=title,
                link_url=link.href
            )

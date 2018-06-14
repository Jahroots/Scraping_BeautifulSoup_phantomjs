# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin


class Tfilm(VideoCaptureMixin, SimpleScraperBase):
    BASE_URL = 'http://kinobar.net'
    OTHER_URLS = ['http://tfilm.space','http://tfilm.tv', 'http://tfilm.me']

    LONG_SEARCH_RESULT_KEYWORD = 'любовь'
    #LONG_SEARCH_RESULT_KEYWORD = 'blue'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Duplicate of kinobar_net.py')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        # self.media_type_to_category = 'film 0, tv 0'
        self.encode_search_term_to = 'cp1251'
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        # self.requires_webdriver = ('parse',)
        # self.requires_webdriver = True
        # self.showposts = 1

    # def get(self, url, **kwargs):
    #     kwargs['headers'] = {
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0',
    #     }
    #     return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?search={}'.format(search_term)
    def _fetch_no_results_text(self):
        return u'По вашему запросу ничего не найдено. Попробуйте ввести похожие по смыслу слова, чтобы получить лучший результат.'
    def _fetch_next_button(self, soup):
        return None

    def post(self, url, **kwargs):
        return super(Tfilm, self).post(url, allowed_errors_codes=[404], **kwargs)

    def _parse_search_result_page(self, soup):
        for result in soup.select("#allEntries div.mat-title a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        iframe = soup.select_one('#adv_kod_frame')
        if iframe:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
            )
        # soup = get(page_url)
        # wd = self.webdriver()
        # wd.get(page_url)
        # source_url=''
        # try:
        #     source_url = wd.find_element_by_xpath('//div[@id="hdnowPlayer"]/iframe').get_attribute('src')
        # except:
        #     pass
        # if source_url:
        #     index_page_title = self.util.get_page_title(self.get_soup(page_url))
        #     self.submit_parse_result(
        #         index_page_title=index_page_title,
        #         link_url=source_url,
        #     )


    # def _parse_parse_page(self, soup):
        # title = soup.select_one('.info_data strong').text


        # film_id = soup._url.split('/')[-1].split('-')[0]
        # self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
        #                          link_url=link
        #                          )

        # request = urllib2.Request('http://redcyt.com/player.php?id=' + film_id, None,
        #                           {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1', 'Connection': 'Close'})
        # try:
        #     page = urllib2.urlopen(request).read()
        #     code_list = re.findall(';file=(.*?)&', page)
        #     if len(code_list) > 0:
        #         code = code_list[0]
        #         code_url = 'http://gegen-abzocke.com/xml/nstrim/filmin/code.php?code_url=' + code
        #         request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
        #                                                     'Connection': 'Close'})
        #         hash = urllib2.urlopen(request2).read()
        #
        #         # TODO    final urls looks like
        #         # http://5.63.144.252/dl/a80854c9134bc6b7a7ced8f4435c07a5/ma/40689.flv
        #         # where IP is rotating
        #         # a80854c9134bc6b7a7ced8f4435c07a5 - hash
        #         # 40689 - same id as in soup._url
        # except Exception as ex:
        #     print ex

        # self.submit_parse_result(index_page_title=soup.title.text.strip(), link_title=title,
        #                          link_url='http://redcyt.com/player.php?id=' + film_id
        #                          )

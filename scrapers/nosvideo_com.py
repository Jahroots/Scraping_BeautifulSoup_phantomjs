# coding=utf-8

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
import re, time
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase


class NosVideo(SimpleGoogleScraperBase):
    BASE_URL = 'http://nosvideo.com'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True
    USER_NAME = 'Reat1950'
    PASSWORD = 'Voo4zai9m'
    EMAIL = 'travisjegan@rhyta.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # self.requires_webdriver = ('parse', )
        # self.webdriver_type = 'phantomjs'  # TODO need to fix and test PARSE()

        raise NotImplementedError('The website becomes and OSP, without any relevant information')

    def __clear_alert(self, wd):
        try:
            WebDriverWait(wd, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
            alert = wd.switch_to.alert
            alert.accept()
        except TimeoutException:
            pass


    def _form_parser(self, soup, search_type=None, form_name=None, form_id=None):
        """

        :param search_type: name or id or both
        :param form_name: form name value
        :param form_id: form id value
        :return:
        """
        form = ''
        input_fields_dic = {}
        action = None
        method = 'get'
        if search_type:
            if search_type.lower() == 'name':
                if form_name:
                    form = soup.find('form', {'name': form_name})
            elif search_type.lower() == 'id':
                if form_id:
                    form = soup.find('form', {'id': form_id})
            elif search_type.lower() == 'both':
                if form_name and form_id:
                    form = soup.find('form', {'name': form_name, 'id': form_id})
        else:
            form = soup.find('form')
        if not form:
            form = soup
        else:
            action = form.get('action','')
            method = form.get('method','get')

        # We extract inputs of following types.
        typelist = ["text", "radio", "checkbox", "password", "file", "image", "hidden", "textarea"]
        input_fields = form.find_all('input', {'type': typelist})

        for elem in input_fields:
            name =  elem.get('name', None)
            if name:
                value = elem.get('value', '')
                input_fields_dic[name] = value

        return input_fields_dic, method, action

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        time.sleep(11)
        input_field_dic, method, action = self._form_parser(soup)
        if input_field_dic:
            input_field_dic['referer'] = 'https://www.google.ru/'
            input_field_dic['imhuman'] = 'Proceed to video'
            name = ''
            if 'fname' in input_field_dic:
                name  = input_field_dic['fname']
            links_page = self.post(self.util.canonicalise(self.BASE_URL,action), data=input_field_dic)
            pat = re.compile(r"\'X7\':\'(http[s]?://(?:[a-zA-Z./]|[0-9])*)+")
            links = re.findall(pat, links_page.text)

            if links and len(links)>0:
                link = links[0]
                if link:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=name
                                             )

            else:
                input_field_dic, method, action = self._form_parser(self.make_soup(links_page.content))
                if input_field_dic:
                    if 'file_code' in input_field_dic:
                        file_code = input_field_dic['file_code']
                        if file_code:
                            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=self.BASE_URL+'/embed/'+file_code,
                                                 link_title=name
                                                 )


        #exit()
        # wd = self.webdriver()
        # print parse_url
        # wd.get(parse_url)
        # but = wd.find_element_by_css_selector('input#btn_download')
        # but.click()
        # try:
        #     button = wd.find_element_by_css_selector('div.download-timer a')
        #     button.click()
        #     self.__clear_alert(wd)
        #     for handle in wd.window_handles:
        #         wd.switch_to.window(handle)
        #         self.__clear_alert(wd)
        #         if not wd.current_url.startswith(self.BASE_URL):
        #             wd.close()
        #     wd.switch_to_window(wd.window_handles[0])
        #     self.__clear_alert(wd)
        #     video_block = wd.find_element_by_css_selector('div.pageSectionMainInternal')
        #     video_block.click()
        #
        #     title = wd.title
        #
        #     for iframe in wd.find_elements_by_tag_name('iframe'):
        #         src = iframe.get_attribute('src')
        #         if src.startswith(self.BASE_URL):
        #             wd.switch_to_frame(iframe)
        #             for video in wd.find_elements_by_tag_name('video'):
        #                 # print video.get_attribute('innerHTML')
        #                 if video.get_attribute('src'):
        #                     self.submit_parse_result(link_url=video.get_attribute('src'),
        #                                              index_page_title=title,
        #                                              )
        #                 else:
        #                     for src in wd.find_elements_by_tag_name('source'):
        #                         self.submit_parse_result(link_url=src.get_attribute('src'),
        #                                                  index_page_title=title,
        #                                                  )
        #         wd.switch_to_window(wd.window_handles[0])
        # except selenium.common.exceptions.NoSuchElementException:
        #     pass

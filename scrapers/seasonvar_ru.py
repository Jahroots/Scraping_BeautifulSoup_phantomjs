#coding=utf-8
import bs4
import json
import re
import selenium

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import VideoCaptureMixin


class SeasonVarRu(SimpleScraperBase, VideoCaptureMixin):

    BASE_URL = 'http://seasonvar.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        # self.requires_webdriver = ('parse', )
        #
        # self._request_size_limit = (1024 * 1024 * 5)  # Bytes

    # def _fetch_search_url(self, search_term, media_type, page=None):
    #     """
    #     Return a GET url for the search term; this is common, but you
    #      will often need to override this.
    #     """
    #     return self.BASE_URL + "/search?q=" + self.util.quote(search_term)

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return self.BASE_URL + '/?mode=search&query={}&page={}'.format(search_term, page)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _fetch_no_results_text(self):
        return u'ничего не найдено'

    # def _fetch_next_button(self, soup):
    #     checked = soup.select_one('div.pages a.checked')
    #     for sibling in checked.next_siblings:
    #         try:
    #             href = sibling.href
    #         except AttributeError:
    #             pass
    #         else:
    #             if href:
    #                 return self.BASE_URL + href
    #     return None


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.pgs-search-info'):
            title_content = result.select_one('a')
            self.submit_search_result(
                link_url=self.BASE_URL + title_content['href'],
                link_title=title_content.text,
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def _video_player_classes(self):
        return []

    def _video_player_ids(self):
        return ['player_wrap', ]

    def use_embed_element(self):
        return False

    def _trigger_container(self, container, driver, action='play'):
        """
        Overwritten maximize before clicking - there's a little overlay that
        breaks junk on a smaller screensize.
        """

        # maximizing pushes it out of the way.
        driver.maximize_window()

        chain = selenium.webdriver.common.action_chains.ActionChains(driver)
        elementsize = container.size
        x_offset = elementsize['width'] / 2
        y_offset = elementsize['height'] / 2

        chain.move_to_element_with_offset(
            container,
            x_offset,
            y_offset,
        )
        chain.click()
        chain.perform()


    # def parse(self, parse_url, **extra):
    #     # Pages contain iframes as well
    #     super(SimpleScraperBase, self).parse(parse_url, **extra)
    #
    #     # Slurp any streaming :-)
    #     urls = self._capture_video_urls(parse_url)
    #     for url in urls:
    #         self.submit_parse_result(
    #             link_url=url
    #         )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        secure_mark_text = re.search("""secureMark\': \'(.*)\',""", soup.text)
        id_num = soup._url.split('/')[-1].split('-')[1]
        if secure_mark_text:
            secure_mark = secure_mark_text.groups()[0]
            list_page = self.get('http://seasonvar.ru/playls2/{}/trans/{}/list.xml'.format(secure_mark, id_num)).text
            playlist_urls = json.loads(list_page)['playlist']
            for playlist_url in playlist_urls:
                url = playlist_url['file']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=url,
                    series_season=series_season,
                    series_episode=series_episode,
                )




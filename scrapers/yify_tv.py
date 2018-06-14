# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, WebDriverException


class Yify_tv(SimpleScraperBase):
    BASE_URL = 'http://yify.bz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    REQUIRES_WEBDRIVER = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 403, 104], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'The list is empty!'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', attrs={'aria-label':'Next'})
        if next_button:
            return next_button['href']
        else:
            return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div[class="soe22"] a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def extract_link(self, dr):
        video_url = None
        try:
            video_url = dr.find_element_by_xpath('//div[@id="player"]//video[@class="jw-video jw-reset"]')
            video_url = video_url.get_attribute('src')
        except NoSuchElementException:
            pass
        if video_url:
            return video_url

    def extract_links(self, parse_url):
        dr = self.webdriver()
        dr.get(parse_url)
        bts = dr.find_elements_by_partial_link_text("Mirror")
        links = set()
        for bt in bts:
            try:
                bt.click()
            except (ElementNotVisibleException, WebDriverException):
                dr.find_element_by_xpath('//div[@class="videoPlayer"]').click()
                time.sleep(3)
                try:
                    bt.click()
                except (ElementNotVisibleException, WebDriverException):
                    continue
            time.sleep(10)
            iframe = dr.find_element_by_xpath("//iframe[@id='playeriframe']")
            dr.switch_to_frame(iframe)
            video_url = self.extract_link(dr)
            dr.switch_to_default_content()
            if not video_url:
                video_url = self.extract_link(dr)
            links.add(video_url)
        return links

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        links = self.extract_links(parse_url)
        for link in links:
            if link:
                self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

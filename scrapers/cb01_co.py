# coding=utf-8
import re, json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class Cb01Co(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://cb-01.com'
    OTHER_URLS = ['https://cb-01.net', 'https://www.cb01.co', 'https://www.cb01.uno']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'U3yQWfPf'

    def setup(self):
        super(self.__class__, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return 'Nessun risultato trovato'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text="Succ →")
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('div[class="ultimigallery"]'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def replace_all(self, decoded_text, dictionary):
        for i, j in dictionary.iteritems():
            decoded_text = decoded_text.replace(i, j)
        return decoded_text

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        url = soup.select_one('div.videodet').find('iframe')
        if url:
            url = url['src']
            self.log.info('url : %s', url)
            if url.startswith('//'):
                url = 'https:' + url

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode
            )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin
import re

class MosalslCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://mosalsl.com'
    OTHER_URLS = ['http://www.mosalsl.com','http://mosalsl.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term) #'{base_url}/index.php/search/?search_paths%5B%5D=&query={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'There were no results found'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li[itemprop="url"] a[rel="next"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="page-content list-related"] ul li')

        if not results and len(results) == 0:
            return  self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            title = title.text
            series_season, series_episode = self.util.extract_season_episode(title)

        scripts = soup.select('ul.servers-tabs li script')

        for script in scripts:
            results = self.util.find_urls_in_text(script.text)
            for result in results:
                if 'http' not in result:
                    result = 'http' + result

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
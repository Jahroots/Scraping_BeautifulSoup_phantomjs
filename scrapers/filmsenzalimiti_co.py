# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class FilmsenzalimitiCo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.filmsenzalimiti.cool'
    OTHER_URLS = ['http://www.filmsenzalimiti.click', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text='»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.find_all('div', 'post-item-side')
        any_results = False
        for block in blocks:
            link = block.find('a')['href']
            title = block.find('a').text
            self.submit_search_result(
                    link_url=link,
                    link_title=title,
                )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for episode_link in soup.find_all('a', 'external'):
            link = episode_link['href']
            title = soup.find('h2', 'film-title').text.strip()
            if 'http://www.altadefinizione01.uno' in link or 'filmtv.it' in link or self.BASE_URL in link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=title
            )
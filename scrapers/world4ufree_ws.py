# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.extras import CloudFlareDDOSProtectionMixin


class World4ufreeWs(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://world4ufree.to'
    OTHER_URLS = ['https://world4ufree.ws']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'


    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '/?s=man'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Next  →')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('ul#loop li h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        for link in soup.select('div.entry a'):
            if link['href'].endswith('jpg') or 'imdb.com' in link['href'] or 'blogspot.com' in link['href']\
                    or 'world4ufree' in link['href']:
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['href'],
                link_text=link.text,
                )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase, CloudFlareDDOSProtectionMixin
import time

class OneClickWatch(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://oneclickwatch.ws'
    OTHER_URLS = ['http://oneclickwatch.org']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def setup(self):
        raise NotImplementedError('Connection TimeOut')

    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '/?s=man'

    def _fetch_no_results_text(self):
        return u'but you are looking for something that'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'nextpostslink')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post h2.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        image = None
        img = soup.find('div.entry img')
        if img:
            image = img['src']
        for link in soup.select('div.entry a'):
            if link['href'].endswith('jpg'):
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['href'],
                link_text=link.text,
                image=image,
                )

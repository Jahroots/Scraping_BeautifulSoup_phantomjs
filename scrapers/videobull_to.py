# -*- coding: utf-8 -*-
import base64
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class Videobull(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://videobull.to'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        raise NotImplementedError('Website not Available')

    def _fetch_no_results_text(self):
        return 'There are no episodes now, please try another'

    def _fetch_next_button(self, soup):
        # Only return the next page if there are results.
        if not soup.select('.postcontent h6 a'):
            return
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.contentarchivetitle a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('.contentlink a'):

            # http://videobull.to/wp-content/themes/videozoom/external.php?title=aHR0cDovL3d3dy5ub3ZhbW92LmNvbS92aWRlby9mNTU3Z25HMzVYa0hjYzU4YTc4MmZkNDM4&linkfrom=novamov.com
            url = link.href
            start = url.find('external.php?title=') + 19
            stop = url.find('&linkfrom=')
            url = url[start:stop]
            url = base64.b64decode(url)

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=url,
                link_title=link.text,
                )

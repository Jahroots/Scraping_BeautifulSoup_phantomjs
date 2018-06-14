# coding=utf-8

from sandcrawler.scraper import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class CineBlog01(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    OTHER_URLS = ['http://cineblog01.li', 'http://www.cineblog-01.club', 'http://www.cineblog-01.site']
    BASE_URL = 'http://www.cineblog01.cool'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ita"

        self.register_media(self.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _parse_search_result_page(self, soup):
        for lnk in soup.select('.post-title > a'):
            self.submit_search_result(
                link_url=lnk.href,
                link_title=lnk.text
            )

    def _fetch_no_results_text(self):
        return u'No matching results'

    def _fetch_next_button(self, soup):
        next = soup.find('a', rel='next')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.blogtitle > h3').text

        for link in soup.select('td .external'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title
                                     )

        for fr in soup.find_all('iframe', {'width': "607"}):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=fr['src'],
                                     link_title=title
                                     )

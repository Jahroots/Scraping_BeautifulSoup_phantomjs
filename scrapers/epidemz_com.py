#coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperFetchException
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class EpidemzCom(CloudFlareDDOSProtectionMixin, OpenSearchMixin, SimpleScraperBase):

    BASE_URL = 'http://epidemz.co'
    OTHER_URLS = ['http://epidemz.net', 'http://epidemz.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.proxy_region='nl'
        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    def _parse_search_result_page(self, soup):
        results = soup.select('div.shortstory h1 a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            image = None
            img = result.parent.parent.find('img')
            if img:
                image = img['src']
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                image=image,
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.quote a'):
            try:
                if link.href.startswith(self.BASE_URL):
                    continue
                followed = self.get(self.BASE_URL + link['href'])
            except ScraperFetchException:
                pass
            else:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=followed.url,
                                         link_title=link.text,
                                         )


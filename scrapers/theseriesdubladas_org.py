# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin
import re

class TheseriesdubladasOrg(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://theseriesdubladas.org'
    OTHER_URLS = ['http://www.theseriesdubladas.org']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term) + '&x=0&y=0'

    def _fetch_no_results_text(self):
        return None#u'Desculpe, mas não encontramos resultados para sua palavra-chave'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.link-next a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):

        results = soup.select('p a.more-link')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('p a.more-link'):
            link = result#.select_one('a')
            if link and link.href:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        results = soup.find('a', text=re.compile(r'Download'))
        if results:
            results = results.parent.find_all('a')
            for link in results:

                self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text,
                    )

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

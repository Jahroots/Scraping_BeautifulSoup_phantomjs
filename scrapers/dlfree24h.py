# -*- coding: utf-8 -*-
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DLFree24HCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://dlfree24h.com'
    OTHER_URL=['http://dlfree24h.net']

    LONG_SEARCH_RESULT_KEYWORD = 'girl'

    USERNAME = 'sandyc'
    EMAIL = 'dlfree@myspoonfedmonkey.com'
    PASSWORD = 'bn23nlsdlkfsd'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'vie'  # Google thinks afrikaans... but it's
        # vietnamese

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(DLFree24HCom, self).get(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def post(self, url, **kwargs):
        return super(DLFree24HCom, self).post(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'


    def _parse_search_result_page(self, soup):
        # print soup
        for result in soup.select('div#dle-content div[class="base shortstory"] h3.btl a'):
            self.submit_search_result(
                link_url=result['href'].lower(),
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def parse(self, parse_url, **extra):
        # Ugh - login is kind of silly.
        # "Guests have no access to this part of the site."
        # "MEMEBERS have no access to this part of the site."
        # self._login()
        return super(DLFree24HCom, self).parse(parse_url, **extra)

    def _parse_parse_page(self, soup):
        content = soup.select('div.maincont')
        # self.show_in_browser(soup)
        if content:
            for url in self.util.find_urls_in_text(
                    unicode(content[0]), skip_images=True):
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                         link_url=url,
                                         )

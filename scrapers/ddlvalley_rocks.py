# -*- coding: utf-8 -*-
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, \
    SimpleScraperBase, \
    ScraperBase, CachedCookieSessionsMixin



class DDLValleyRocks(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.ddlvalley.me'

    OTHER_URLS = ['http://www.ddlvalley.cool', 'http://www.ddlvalley.rocks', ]

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SEARCH_TERM = ''

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(self.MEDIA_TYPE_TV)
        self.register_media(self.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        super(DDLValleyRocks, self).search(search_term, media_type, **extra)

    def _fetch_search_url(self, search_term, media_type):
        return '%s/search/%s/' % \
               (self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'Sorry, no posts matched your criteria.'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a.nextpostslink')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('.pb.fl h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def parse(self, page_url, **extra):
        for soup in self.soup_each([page_url]):
            links = soup.select('div.cont.cl p a')

            for link in [lnk for lnk in links if "data-wpel-link" in lnk.attrs]:
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_title=link.text,
                                         link_url=link.get('href'))

    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '/search/' + self.SEARCH_TERM + '/'

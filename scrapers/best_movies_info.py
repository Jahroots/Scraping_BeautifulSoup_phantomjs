# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class BestMoviesInfo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://best-movies.info'
    TRELLO_ID = 'vON1s2VE'

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, 404, 503, ], **kwargs)

    def _fetch_no_results_text(self):
        return u'No suitable matches were found'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?keywords=' + \
               self.util.quote(search_term) + \
               '&terms=all&author=&attr_id=0&sc=1&sf=titleonly&sr=topics&sk=t&sd=d&st=0&ch=0&t=0&submit=Search'

    def _fetch_next_button(self, soup):
        # self.show_in_browser(soup)
        link = soup.find('a', text='Next')
        self.log.debug('--------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for link in soup.select('a.topictitle'):
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'][1:],
                link_title=link.text,
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        #self.log.debug(soup)

        title = soup.select_one('#page-body > h2').text

        for a in soup.select('blockquote.uncited a[href*="./abbcode_page.php?mode"]'):
                link = a.href.replace('./', '/').split('&sid')[0]
                sl = self.get(self.BASE_URL + link).url
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=sl,
                    link_title=title,
                )

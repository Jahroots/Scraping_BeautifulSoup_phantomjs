# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, \
    CloudFlareDDOSProtectionMixin, \
    ScraperBase


class DnBlogBiz(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://dnmedia.biz'

    LONG_SEARCH_RESULT_KEYWORD = 'Amelie'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "deu"
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        raise NotImplementedError('No longer this blog relevant')

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(
            self.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            self.URL_TYPE_LISTING,
            self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        raise NotImplementedError('Website Not available')

    # def _fetch_search_url(self, search_term, media_type):
    #     return self.BASE_URL + '/search/' + search_term

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        return

    def _parse_search_result_page(self, soup):
        for lnk in soup.select('.entry-title'):
            self.submit_search_result(
                link_url=lnk['href'],
                link_title=lnk.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.title.text.strip()

        for span in soup.find_all('span', {'data-enigmad': "n"}):
            for url in self.util.find_urls_in_text(eval("u'%s'" % span['data-enigmav'].replace('-', '\\u00'))):
                self.submit_parse_result(index_page_title=title,
                                         link_url=url,
                                         link_text=title,
                                         )

        for link in soup.select('a.tbtns01'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href.strip(),
                                     link_text=link.text,
                                     )

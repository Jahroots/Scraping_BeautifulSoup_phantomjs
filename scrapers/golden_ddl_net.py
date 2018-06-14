# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class GoldenDdl(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.golden-ddl.in'
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    def setup(self):
        raise NotImplementedError('Deprecated. The domain is for sale')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        # OpenSearchMixin advanced search settings
        self.bunch_size = 40
        self.media_type_to_category = 'film 0, tv 0'
        # self.encode_search_term_to = 'cp1251'
        self.showposts = 0


    def _get_search_results(self, search_term, page=1):

        return self.post_soup(self.BASE_URL + '/index.php?do=search', data=dict(do='search',
                                                                                subaction='search',
                                                                                search_start=page,
                                                                                full_search='0',
                                                                                result_from=1,
                                                                                story=self.util.quote(
                                                                                    search_term),
                                                                                ))

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        self.page = 1

        soup = self._get_search_results(search_term)

        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)



    def _fetch_no_results_text(self):
        return u'The search did not return any results.'

    def _parse_search_result_page(self, soup):
        for result in soup.select(".heading a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))
        nextlink = soup.select('a#nextlink')
        if nextlink and self.can_fetch_next():
            self.page += 1
            self._parse_search_result_page(
                self._get_search_results(self.search_term, self.page))

    def _parse_parse_page(self, soup):
        id_ = soup._url.split('/')[-1].split('-')[0]
        title = soup.title.text

        for link in soup.select('#news-id-{} div a'.format(id_)):
            if link.attrs.get('target', '') == "_blank":  # and len(link.href.split('/')) > 3:
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_title=title,
                                         link_url=link.href)

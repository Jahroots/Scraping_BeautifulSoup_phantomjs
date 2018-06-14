# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmeonlineBiz(SimpleScraperBase):
    BASE_URL = 'http://www.filmeonline.biz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _fetch_search_url(self, search_term, media_type):
        return u'{}/?s={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Îmi pare rău, nu am putut găsi'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[class="next page-numbers"]')
        if next_button:
            return next_button.href
        return None

    def __buildlookup(self):
        lookup = {}
        #mainsoup in self.soup_each([self.BASE_URL, ])
        mainsoup = self.get_soup(self.BASE_URL)
        for i in range(1, 125):
            for serial_link in mainsoup.select('a[href*="' + self.BASE_URL + '"]'):
                lookup[serial_link.text.lower().strip() + ' ' + serial_link.text] = serial_link.href.strip()

            next_button = self._fetch_next_button(mainsoup)
            if next_button and self.can_fetch_next():
                mainsoup = self.get_soup(next_button)
            else:
                break
        return lookup

    def search(self, search_term, media_type, **extra):
        self._request_connect_timeout = 600
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term) or search_term in term:
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )

                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for iframe in soup.select('iframe'):
            url = iframe['src']
            if url.startswith('//'):
                url = 'http:' + url
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url

            )

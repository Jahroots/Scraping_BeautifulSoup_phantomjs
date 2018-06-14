# coding=utf-8


from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Mazika2dayCom(SimpleScraperBase):
    BASE_URL = 'http://mazika2day.com'
    OTHER_URLS = ['http://forums.mazika2day.com']
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?search={}'.format(search_term.replace(' ', '+'))

    def _fetch_no_results_text(self):
        return u'لا يوجد مواضيع'

    def _fetch_next_button(self, soup):
        link = soup.select_one('ul.pagination a[rel="next"]')

        return link['href'] if link else None

    def _parse_search_result(self, soup, search_term):
        results = soup.select('a[class="item grey1"]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        next_button = self._fetch_next_button(soup)


        for link in results:
            soup = self.get_soup(link.href)
            links = soup.select('div.download a')
            for link in links:
                self.submit_search_result(
                        link_url=link.href,
                        link_title=soup.select_one('h1').text
                    )


        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result(soup, search_term)

    def search(self, search_term, media_type, **extra):
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_result(soup, search_term)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.servers a')
        for result in results:
            link = result['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
            )
        results = soup.select('div.downloadlinks a')
        for result in results:
            link = result['href']
            soup = self.get_soup(self.BASE_URL + link)
            link = soup.select_one('a[href*="/getlink/"]')
            soup = self.get_soup(self.BASE_URL + link.href)

            link = soup.select_one('div.pagescontainer a')
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                )


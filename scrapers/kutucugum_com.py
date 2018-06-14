# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class KutucugumCom(SimpleScraperBase):
    BASE_URL = 'http://kutucugum.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Deprecated. Website cannot be reached')

    def _do_search(self, search_term, page=1):
        return self.post_soup(
            self.BASE_URL + '/action/SearchFiles',
            data={'Mode':'Gallery', 'Type':'', 'Phrase':'{}'.format(self.util.quote(search_term)),
                  'SizeFrom':'0', 'SizeTo':'0', 'Extension':'','ref':'pager', 'pageNumber':page,
                  }
        )

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        first_page = self._do_search(search_term)
        if unicode(first_page).find('No results found') >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(first_page)
        page = 1
        while self.can_fetch_next():
            page += 1
            soup = self._do_search(
                search_term,
                page
            )
            self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h2.name a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=self.BASE_URL+result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2').text.strip()
        index_page_title = self.util.get_page_title(soup)
        movie_link = soup.select_one('div#fileDetails')['data-player-file']
        self.submit_parse_result(
            index_page_title=index_page_title,
            link_url=movie_link,
            link_text=title,
        )
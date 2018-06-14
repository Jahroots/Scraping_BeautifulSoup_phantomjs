# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmtornadoEu(SimpleScraperBase):
    BASE_URL = 'https://filmtornado.cc'
    OTHER_URLS = ['http://filmtornado.cc', 'https://onlinefilmekneked.ru']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hun'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_PARSE = True
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'AflVuhEy'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL +'/search.php'

    def _fetch_no_results_text(self):
        return u'Nem talalhato film'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('None')
        if next_button:
            return next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        self._parse_search_result_page(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="mt"] a[class*="dvd hun"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:

            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )


    def _parse_parse_page(self, soup):
        div = soup.select_one('div[onclick]')
        if div:
            for url in self.util.find_urls_in_text(div['onclick']):
                aux_soup = self.get_soup(url)
                index_page_title = self.util.get_page_title(aux_soup)
                for link in aux_soup.select('tr[data-href]'):
                    aux_soup = self.get_soup(link['data-href'])
                    iframe = aux_soup.select_one('#movieframe')
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=iframe['src'],
                        link_title=link.text,
                    )



    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL + '/search.php',
            data={
                'search':search_term})

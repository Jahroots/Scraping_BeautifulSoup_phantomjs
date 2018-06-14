# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmehdgratisBiz(SimpleScraperBase):
    BASE_URL = 'http://www.filmehdgratis.biz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Nu a fost gasit nici un film cu numele de'

    def _fetch_next_button(self, soup):
        next_button = self.BASE_URL + '/page/' + str(self.page) +'/?s=' + self.util.quote(self.search_term)
        self.page += 1

        return next_button

    def search(self, search_term, media_type, **extra):
        self.page = 2
        self.search_term = search_term

        super(self.__class__, self).search(search_term, media_type, **extra)
        
    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('input[name="titulo"]')
        for link in soup.select('p iframe'):
            src = link['src']
            if src.find('http') == -1:
                src = 'http:' + src

            self.submit_parse_result(
                index_page_title = index_page_title,
                link_url = src,
                link_title = title.value
            )

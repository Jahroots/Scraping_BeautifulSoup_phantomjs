# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class IandyouPw(SimpleScraperBase):
    BASE_URL = 'http://funloty.com'
    OTHER_URLS = ['http://iandyou.pw']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'heb'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def _fetch_search_url(self, search_term, media_type):
        self.search_url = '{base_url}/?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)
        self.one = False
        return self.search_url

    def _fetch_no_results_text(self):
        return u' TODO '

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li.next a')
        if next_button:
            return self.search_url + next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('h3 a')

        if (not results or len(results) == 0) and not self.one:
            return self.submit_search_no_results()

        self.one = True

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('a[href*="away"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= 'http://' + link.text,
                link_title=link.title,
            )

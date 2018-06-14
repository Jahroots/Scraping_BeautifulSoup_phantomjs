# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, VBulletinMixin

class DuckloadWs(VBulletinMixin, SimpleScraperBase):
    BASE_URL = 'http://www.duckload.ws'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'star wars'

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            u'{}/forum/search.php?do=process'.format(self.BASE_URL),
            data={
                'securitytoken': 'guest',
                'do': 'process',
                'query': search_term,
                'submit.x': 0,
                'submit.y': 0
            }
        )
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'Sorry - no matches. Please try some different terms.'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[rel="next"]')
        if next_button:
            return u'{}/forum/{}'.format(self.BASE_URL, next_button.href)
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.thread h3.searchtitle a'):
            self.submit_search_result(
                link_url=u'{}/forum/{}'.format(self.BASE_URL, result.href),
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
    
        for link in self.util.find_urls_in_text(str(soup.select_one('div.content') or '')):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
            )

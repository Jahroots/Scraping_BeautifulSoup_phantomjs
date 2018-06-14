# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class GigabaseCom(SimpleScraperBase):
    BASE_URL = 'http://www.gigabase.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/{l}/{search_term}'.format(base_url=self.BASE_URL, search_term=search_term, l=search_term[0])

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a',text='→')
        if next_button:
            return soup._url+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.find_all('li', attrs={'style':'padding-bottom: 1em;'}):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()
    def _parse_parse_page(self, soup):
        title = soup.select_one('h2')
        if title and title.text:
            title = title.text

        index_page_title = self.util.get_page_title(soup)
        link = soup._url
        self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=title
            )

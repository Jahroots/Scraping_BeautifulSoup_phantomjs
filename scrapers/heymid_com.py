# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HeymidCom(SimpleScraperBase):
    BASE_URL = 'http://heymid.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'kor'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[class="next page-numbers"]')
        if next_button:
            return next_button.href
        else:
            return None

    def _parse_search_result_page(self, soup):
        results = soup.select('#post-items article h2.entry-title a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.log.debug(link.href)
            self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.embed-container iframe'):
            if 'http' in link['src']:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                )

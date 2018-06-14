# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class StreamallthisIs(SimpleScraperBase):
    BASE_URL = 'http://picwash.com'
    OTHER_URLS = ['http://streamallthis.is']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

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

        results = soup.select('ul.recent-posts div.post-thumb a[data-wpel-link]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
            )



    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)

        links = soup.select('a[href*="file"]')
        for link in links:
            href = link.href
            if 'http' not in href:
                href = self.BASE_URL + href
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=href
            )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FlowerBlogOrg(SimpleScraperBase):
    BASE_URL = 'https://www.flower-blog.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'NICHTS GEFUNDEN.'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a.next')
        return link and link.href or None

    def search(self, search_term, media_type, **extra):
        # This page breaks soups parser - cut it on a mid point and ... yeah.
        response = self.get(self._fetch_search_url(search_term, media_type))
        body = response.text.split(u'Suchergebnisse fü')[-1]
        return self._parse_search_results(self.make_soup(body))


    def _parse_search_result_page(self, soup):
        results = soup.select('h2.entry-title a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for link in results:
            self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(link, 'img'),
            )

    def parse(self, parse_url, **extra):
        # Again - broken parser - cut out what we need.
        response = self.get(parse_url)
        body = response.text.split('<article')[-1]
        soup = self.make_soup(body)
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.entry-content a'):
            if 'direct-download.php' not in link.href:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                )

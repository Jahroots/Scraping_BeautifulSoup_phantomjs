# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class VediserieCom(SimpleScraperBase):
    BASE_URL = 'http://www.vediserie.tv'
    OTHER_URLS = ['http://www.vediserie.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.imagen a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.parent.select_one('h2').text,
                image = link.parent.select_one('img')['src']
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        selects = soup.select('select[class="selEp"]')
        for index, select in enumerate(selects):
            season = index + 1
            chapters = select.select('option[data-link]')
            for index, chapter in enumerate(chapters):
                episode = index
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=chapter['data-link'],
                    link_title=chapter.text,
                    season = season,
                    episode = episode
                )



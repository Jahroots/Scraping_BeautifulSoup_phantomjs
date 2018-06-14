# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class CinemaliberoCom(SimpleScraperBase):
    BASE_URL = 'https://www.cinemalibero.club'
    OTHER_URLS = ['http://www.cinemalibero.tv', 'http://www.cinemalibero.co', ]

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[520], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Non ho trovato risultati con il testo ricercato"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', 'next')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('a.locandina'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('section.block p a')
        for result in results:
            movie_link = result['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
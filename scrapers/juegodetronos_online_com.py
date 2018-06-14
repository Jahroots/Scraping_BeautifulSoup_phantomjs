# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class JuegodetronosOnlineCom(SimpleScraperBase):
    BASE_URL = 'http://juegodetronos-online.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'el'

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?dato={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No se han encontrado resultados'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Siguiente')
        if next_button:
            return self.BASE_URL + '/' + next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('#ancla_resultados h2'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('ul li a[href*="web.juegodetronos"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

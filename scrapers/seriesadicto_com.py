# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SeriesadictoCom(SimpleScraperBase):
    BASE_URL = 'http://seriesadicto.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No se han encontrado ninguna serieEnvia'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('a.thumbnail'):
            result_soup = self.get_soup(self.BASE_URL+results['href'])
            for links in result_soup.select('a.color4'):
                link = self.BASE_URL+links['href']
                title = links.text
                season, episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=link,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('a.btn'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_text=title,
                series_season=season,
                series_episode=episode
            )
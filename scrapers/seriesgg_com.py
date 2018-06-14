# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SeriesggCom(SimpleScraperBase):
    BASE_URL = 'http://seriesgg.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/buscar/?&q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.panel-body div.thumbnail'):
            link = result.select_one('a')
            movie_soup = self.get_soup(link.href)
            for movie_link in movie_soup.select('table.table tbody a'):
                self.submit_search_result(
                    link_url=movie_link.href,
                    link_title=movie_link.text,
                    image=result.find('img')['data-original'],
                )
                found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        script_text = self.util.find_urls_in_text(soup.find(text=re.compile('Lista de episodios')).find_next('script').
                                                  text.split('lctmr=')[-1].split(';')[0].replace('\\', ''))
        for script_link in script_text:
            if self.BASE_URL in script_link:
                movie_soup = self.get_soup(script_link)
                movie_script_text = self.util.find_file_in_js(movie_soup.find_all('script')[-1].text)
                for movie_script_link in movie_script_text:
                    movie_link = self.get_redirect_location(movie_script_link.replace('\\', ''))
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=movie_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=script_link,
                    link_title=script_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

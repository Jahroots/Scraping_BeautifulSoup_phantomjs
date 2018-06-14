# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Filme5Net(SimpleScraperBase):
    BASE_URL = 'http://filme5.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/cauta?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found =0
        for result in soup.select('div#movies')+soup.select('div#series'):
            link = result.select_one('a')
            if link:
                if '/seriale-online/' in link.href:
                    for series_link in self.get_soup(link.href).select('a.sezon'):
                        for ep_link in self.get_soup(series_link.href).select('ul#episode-list'):
                            link = ep_link.select_one('a')
                            self.submit_search_result(
                                link_url=link.href,
                                link_title=link.text,
                                image=self.util.find_image_src_or_none(ep_link, 'img'),
                            )
                else:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('td.name a'):
            movie_links = self.util.find_urls_in_text(link['data-bind'])
            for movie_link in movie_links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

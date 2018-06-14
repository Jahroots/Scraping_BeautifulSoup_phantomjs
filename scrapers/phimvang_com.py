# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PhimvangCom(SimpleScraperBase):
    BASE_URL = 'http://phimvang.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated. Parse results not available')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/tim-kiem?key={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li.pager-next a')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.phim_teaser'):
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
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.videobig div.video_container'):
            script_path = result.find_next('script').text.split("play_url+'")[-1].split("',")[0]
            script_url = 'http://play.phimvang.com'+script_path
            movie_soup = self.get_soup(script_url)
            movie_soup_links = json.loads(movie_soup.text)
            for movie_links in movie_soup_links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_links['url'],
                    link_title=result.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

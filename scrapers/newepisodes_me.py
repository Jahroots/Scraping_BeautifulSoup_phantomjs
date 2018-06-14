# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import json


class NewepisodesMe(SimpleScraperBase):
    BASE_URL = 'http://newepisodes.co'
    OTHER_URLS = ['http://newepisodes.me']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def search(self, search_term, media_type, **extra):
        # A javascript search block.
        search_code = self.get("http://newepisodes.me/search.js").content
        search_json = json.loads(search_code[16:-3])
        results = search_json['pages']
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for result in results:
            if search_regex.match(result['title']):
                soup = self.get_soup('http:' + result['url'])
                for result_block in soup.select('div.list-item'):
                    any_results = True
                    link = result_block.select_one('a')
                    if link:
                        self.submit_search_result(
                            link_url='http:' + link.href,
                            link_title=link.text,
                            image='http:' + result['thumb'],

                        )

        if not any_results:
            self.submit_search_no_results()

    def _load_api_url(self, id):
        url = '{}/embed/{}'.format(self.BASE_URL, id)
        soup = self.get_soup(url)
        results = []
        for iframe in soup.select('iframe'):
            results.append(iframe['src'])
        return results

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')

        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for item in soup.select('div.playlist_inner li'):
            for url in self._load_api_url(item['id']):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    series_season=series_season,
                    series_episode=series_episode

                )

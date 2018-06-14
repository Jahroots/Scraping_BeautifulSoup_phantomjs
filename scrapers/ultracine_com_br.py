# coding=utf-8

from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class UltracineComBr(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.ultracine.com.br'
    OTHER_URLS = ['http://omegafilmeshd.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Website not Available')

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.player-video iframe'):
            link = result['src']
            if 'youtube' in link:
                continue
            movie_soup = self.get_soup(link)
            movie_link = movie_soup.select_one('iframe')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link['src'],
                link_title=movie_link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

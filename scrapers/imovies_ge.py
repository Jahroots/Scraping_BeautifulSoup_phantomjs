# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ImoviesGe(SimpleScraperBase):
    BASE_URL = 'https://www.imovies.cc'
    OTHER_URLS = ['http://imovies.ge']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'geo'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def search(self, search_term, media_type, **extra):
        result = self.get(
            'https://api.imovies.cc/api/v1/search-advanced?filters%5Btype%5D=movie&page=1&per_page=100&keywords={}'.format(
                search_term)
        ).json()
        for result in result['data']:
            self.submit_search_result(
                link_url=u'{}/movies/{}'.format(self.BASE_URL, result['id']),
                link_title=result['primaryName'],
                image=result['poster'],
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = ''
        for h2 in soup.select('h2'):
            title = u'{} {}'.format(title, h2.text)
        if title:
            series_season, series_episode = self.util.extract_season_episode(title)
        for link in soup.select('video#musicvideo source'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

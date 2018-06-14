# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class ItafilmVideo(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.itafilm.tube'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated. Website disabled by administrator.')

    def _fetch_no_results_text(self):
        return u'Ci spiace ma la tua ricerca non ha prodotto alcun risultato'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.main-news'):
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
        movie_links = soup.select('div.session iframe')
        for movie_link in movie_links:
            if 'youtube' in movie_link['src']:
                continue
            link = movie_link['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_text=movie_link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class BestdownloadfreeCom(SimpleScraperBase):
    BASE_URL = 'http://bestdownloadfree.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK,
                    ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated. The website is now an etherium miner.')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Assicurati di avere digitato correttamente tutte le parole'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.thumbnail-post'):
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
        for result in soup.select('div.entry-content a[target="_blank"]'):
            if self.BASE_URL in result.href or 'whatsapp' in result.href:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=result.href,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )

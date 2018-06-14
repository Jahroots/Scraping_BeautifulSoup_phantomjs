# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Movies300mbCom(SimpleScraperBase):
    BASE_URL = 'https://movies-300mb.club'
    OTHER_URLS = ['https://www.movies-300mb.net', 'http://www.movies-300mb.net', 'http://www.movies-300mb.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.nav-previous a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.entry-thumb'):
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

        links = soup.select('div.entry-content i a[target="_blank"]')
        for link in links:
            if link.href:
                mov_link = link.href
                if 'http' not in mov_link:
                    mov_link = 'https:'+mov_link
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=mov_link,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

        links = soup.select('h3 i a[target="_blank"]')
        if links:
            # print links
            for link in links:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )


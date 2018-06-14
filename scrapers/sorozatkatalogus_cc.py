# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SorozatkatalogusCc(SimpleScraperBase):
    BASE_URL = 'https://sorozatkatalogus.cc'
    OTHER_URLS = ['http://sorozatkatalogus.cc']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hun'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}&asl_active=1'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Elnézést, nem találunk a keresési feltételeknek megfelelő eredményt'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h1.entry-title'):
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
        for link in soup.select('div.entry-content iframe'):
            src = link['src']
            if 'http' not in src:
                src = 'http:' + src

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        for link in soup.select('div.entry-content table img'):
            if 'http' in link.find_previous()['href']:
                download_link = link.find_previous()['href'].split('http')[-1]
                link_soup = self.get_soup('http' + download_link)
                movie_link = link_soup.select_one('div.entry-content iframe')
                src = movie_link['src']
                if 'http' not in src:
                    src = 'http:' + src
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src,
                    link_title=movie_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SinemafilmOrg(SimpleScraperBase):
    BASE_URL = 'http://www.hdfilmizle.fun'
    OTHER_URLS = ['http://www.sinemafilm.org']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Aradığınız kriterlere uygun film bulunamadı'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text="İleri »")
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.movie-poster'):
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

        iframes = soup.select('div.video-content iframe')
        for iframe in iframes:
            src = iframe['src']
            if 'http' not in src:
                src = 'http:' +  src
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_text=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )

        links = soup.select('div.keremiya_part a')
        for link in links:
            soup = self.get_soup(link.href)
            iframes = soup.select('div.video-content iframe')
            for iframe in iframes:
                src = iframe['src']
                if 'http' not in src:
                    src = 'http:' + src
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src,
                    link_text=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )


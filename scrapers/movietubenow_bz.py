# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class MovietubenowBz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.movietubenow.bz'
    OTHER_URLS = ['http://www.movietubenow.biz']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.img-serial'):
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
        for link in soup.select('div.section div.box iframe'):
            iframe_link = link['src']
            if iframe_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

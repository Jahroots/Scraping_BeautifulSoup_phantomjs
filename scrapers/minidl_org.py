# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MiniDl(SimpleScraperBase):
    BASE_URL = "http://minidl.org"

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _parse_search_result_page(self, soup):
        for link in soup.select('h2[class="post-title entry-title"] a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_no_results_text(self):
        return 'Sorry, but no results were found for that keyword'

    def _fetch_next_button(self, soup):
        next = soup.select_one('a.nextpostslink')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[class="post-title entry-title"]')
        if title and title.text:
            title = title.text
        series_season, series_episode = self.util.extract_season_episode(title)

        for box in soup.select('p a'):
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=box.href,
                link_title= box.text,
                series_season=series_season,
                series_episode=series_episode,
            )

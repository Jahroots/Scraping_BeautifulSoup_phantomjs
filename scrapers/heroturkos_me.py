# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Heroturkos_Me(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = "http://www.heroturkos.me"

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _parse_search_result_page(self, soup):
        for result in soup.select("div.header"):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for code_box in soup.select('.quote'):
            text = str(code_box).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(text):
                if url.startswith('http'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=url,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

        for url in soup.select('.quote a'):
            if url.startswith_http:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url.href,
                    link_title=url.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Hotfiletrend(SimpleScraperBase):
    BASE_URL = "http://hotfiletrend.com"

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

    def _fetch_search_url(self, search_term, media_type, start=0):
        self.start = start
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/?q={}&search=Search&start={}'.format(search_term, start)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        self.start += 15
        next_button_link = self._fetch_search_url(self.search_term, self.media_type, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('.item table a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_no_results_text(self):
        return 'No results found'

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        series_season, series_episode = self.util.extract_season_episode(title)

        # for link in soup.select('.info table a'):
        #     if not link.href.startswith('/cx.php'):
        #         self.submit_parse_result(
        #             link_url=link.href,
        #             link_title=title,
        #             series_season=series_season,
        #             series_episode=series_episode,
        #         )

        link = self.util.unquote(str(soup).split("document.write(unescape('")[1].split("'));")[0])[9:].split("' ")[0]
        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                 link_url=link,
                                 link_title=title,
                                 series_season=series_season,
                                 series_episode=series_episode,
                                 )


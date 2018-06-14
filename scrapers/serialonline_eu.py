# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SerialonlineEu(SimpleScraperBase):
    BASE_URL = 'http://serialonline.eu'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/show/{}&ajax&p={}'.format(search_term, start)

    def _fetch_no_results_text(self):
        return u'Zatím tady nic není'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        rslts = soup.select('h4.video-title a')
        for result in rslts:
            season, episode = self.util.extract_season_episode(result.text)
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        title = soup.find('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)
        for iframe_link in soup.select('div#video-content iframe'):
            movie_link = iframe_link['src']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_title=title,
                                     link_url=movie_link,
                                     series_season=season,
                                     series_episode=episode,
                                     )

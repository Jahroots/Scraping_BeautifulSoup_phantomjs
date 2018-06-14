# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class LibreStreamCom(SimpleScraperBase):
    BASE_URL = 'http://ls-streaming.com'
    OTHERS_URLS = ['http://libre-stream.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type=None, start=1, end=1):
        self.start = start
        self.end = end
        if start == 1:
            self.search_term = search_term
            return self.BASE_URL + '/index.php?search_start={}&result_from={}&q={}'.format(start, start,
                                                                                         search_term)
        else:
            self.search_term = search_term
            return self.BASE_URL + '/index.php?search_start={}&result_from={}&q={}'.format(start, end, search_term)


    def _fetch_no_results_text(self):
        return u'La recherche n a retourné'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        self.end +=16
        next_button_link = self._fetch_search_url(self.search_term, start=self.start, end=self.end)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        rslts = soup.select('div.hcontent h2')
        for result in rslts:
            season, episode = self.util.extract_season_episode(result.text)
            link = result['onclick'].split("window.location.href='")[-1].strip("'")
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        for iframe_link in soup.select('iframe'):
            title = soup.find('h2').text.strip()
            movie_link = iframe_link['src']
            season, episode = self.util.extract_season_episode(title)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_title=title,
                                     link_url=movie_link,
                                     series_season=season,
                                     series_episode=episode,
                                     )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import base64

class FullStreamLa(SimpleScraperBase):
    BASE_URL = 'http://full-stream.stream'
    OTHER_URLS = ['http://full-stream.live', 'http://full-stream.tv', 'http://full-stream.zone']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    page = 1
    search_term = ''


    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u' Vous pouvez effectuer une nouvelle recherche ou vous pouvez utiliser Le Filtre'

    def _fetch_next_button(self, soup):
        self.page += 1
        return self.BASE_URL + '/page/' + str(self.page) + '?s=' + self.util.quote(self.search_term)

    def search(self, search_term, media_type, **extra):
        self.page = 1
        self.search_term = search_term

        search_url = self._fetch_search_url(search_term, media_type)
        soup = self.get_soup(search_url)
        self._parse_search_result_page(soup)

        next_url = self._fetch_next_button(soup)
        if next_url and self.can_fetch_next():
            soup = self.get_soup(search_url)
            self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        if self._fetch_no_results_text() in unicode(soup):
            return self.submit_search_no_results()

        for result in soup.select('article[class="shortstory cf"]'):
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
        for link in soup.select('#fullstreamlien tr a.link_a'):
            if 'toro' not in link.href:
                try:
                    self.log.debug(link.href)


                    self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link.href,
                            link_title=link.text,
                            series_season=series_season,
                            series_episode=series_episode,
                        )
                except Exception as e:
                    self.log.info(e)

    def get(self, url, **kwargs):
        return super(FullStreamLa, self).get(url, allowed_errors_codes=[404, 503], **kwargs)
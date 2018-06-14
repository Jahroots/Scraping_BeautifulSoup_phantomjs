# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.exceptions import ScraperFetchException

class Zerx_co(SimpleScraperBase):
    BASE_URL = 'http://zerx.club'
    OTHER_URLS = ['http://zerx.co']
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = u'дней'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def head(self, url, **kwargs):
        return self._do_request_action('head', url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?do=search&q=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'К сожалению нам не удалось найти то, что Вы ищете.'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.left')
        self.log.debug('------------------------')
        return link.parent['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('a.o-card__title'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip()
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = None
        try:
            title = soup.select_one('.c-movie__title').text.strip()
        except AttributeError:
            try:
                title = soup.find('h1', itemprop='name').text.strip()
            except AttributeError:
                pass
        if title:
            season, episode = self.util.extract_season_episode(title)

        iframes = soup.select('iframe')
        for iframe in iframes:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=iframe['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     )
        


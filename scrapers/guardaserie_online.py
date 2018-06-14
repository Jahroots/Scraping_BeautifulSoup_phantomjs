#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class GuardaserieOnline(SimpleScraperBase):

    BASE_URL = 'http://www.guardaserie.online/'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u"Nessun risultato per"

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        soup = self.get_soup(self.BASE_URL + '/?s={}'.format(self.util.quote(search_term)))
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        rslts = soup.find_all('a', 'box-link-serie')
        if not rslts:
            self.submit_search_no_results()
        for result in rslts:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.find('p').text
            )

    def _parse_parse_page(self, soup):
        for link in soup.find('div', 'container container-row-stagioni').find_all('span', 'player-overlay'):
            url = link['meta-embed']
            link_title = link['meta-serie']
            season = link['meta-stag']
            episode = link['meta-ep']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url,
                                     link_title=link_title,
                                     series_season=season,
                                     series_episode=episode
                                     )


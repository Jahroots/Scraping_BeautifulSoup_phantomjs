# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WatchSeriesOnlineCh(SimpleScraperBase):
    BASE_URL = 'https://watchseries-online.be'
    OTHER_URLS = ['https://watchseries-online.pl', 'http://watchseries-online.la', 'http://watchseries-online.nl']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        # Nothing, just a blank page - raise the exception in _parse_search_result_page
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?search=&s=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        if link:
            return link['href']
        return None

    def search(self, search_term, media_type, **kwargs):
        self.any_results = False
        super(WatchSeriesOnlineCh, self).search(search_term, media_type, **kwargs)

    def _parse_search_result_page(self, soup):
        results = soup.select('.ddmcc > ul > li > a')
        if not results:
            if not self.any_results:
                self.submit_search_no_results()
            return None

        for result in results:
            self.any_results = True
            season, episode = self.util.extract_season_episode(result.text)
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('table.postlinks tbody div.play-btn a'):

            if 'href' in link.attrs and link.href != '#':
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=soup.select_one('.single_title').text
                                         )

        # links 2 series
        for ser in soup.select('.episodes_left.col-xs-6.pull-left li a'):
            suup = self.get_soup(ser.href)
            self._parse_parse_page(suup)

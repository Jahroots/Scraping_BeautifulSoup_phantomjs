# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class PrimeSeriesTo(SimpleScraperBase):
    BASE_URL = 'http://primeseries.to'
    pag = 2
    USER_AGENT_MOBILE = False
    def setup(self):

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.long_parse = True

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def _fetch_no_results_text(self):
        return 'Sorry we do not have any results for that search'

    def _fetch_next_button(self, soup):
        link = self.BASE_URL + '/search/' + self.util.quote(self.search_term) + '/page/' + str(self.pag)#soup.select_one('a i[class="fa fa-chevron-right"]')
        self.pag += 1
        self.log.debug('------------------------')
        return link

    def _fetch_search_url(self, search_term, media_type, start=None):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def search(self, search_term, media_type, **extra):
        self.pag = 2
        self.search_term = search_term

        soup = self.get_soup(self._fetch_search_url(search_term, media_type))


        if self._fetch_no_results_text() in soup.select_one('#latest-pop-box').text:
            return self.submit_search_no_results()
        results = soup.select('a[class*="link ps-r"]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        next_button = self._fetch_next_button(soup)

        if next_button and self.can_fetch_next() and soup.select_one('a i[class="fa fa-chevron-right"]'):
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        results = soup.select('a[class*="link ps-r"]')
        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text,
            )

    @cacheable()
    def _follow_link(self, url):
        soup = self.get_soup(url)
        link = soup.select_one('a[class="external-play-btn"]')
        return link.href



    def _parse_parse_page(self, soup):

        seasons = soup.select('div.swiper-wrapper div a')
        for season in seasons:
            season_soup = self.get_soup(self.BASE_URL + season['href'])
            episodes = season_soup.select('tr[itemprop="episode"] a')
            for episode in episodes:
                episode_soup = self.get_soup(self.BASE_URL + episode['href'])
                season = None
                episode = None
                title = episode_soup.select_one('h1[class="f-md episode-ttl txt-l"]')
                if title:
                    title = title.text.strip()
                    season, episode = self.util.extract_season_episode(title)
                index_page_title = self.util.get_page_title(soup)

                for link in episode_soup.select('a[class="db link watch-link p2"]'):
                    self.log.warning(link.href)
                    soup = self.get_soup(
                        self.BASE_URL + link['href']
                    )
                    url = soup.select_one('a.external-play-btn')
                    if url:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url = url.href,
                            link_title = title,
                            series_season = season,
                            series_episode = episode
                        )

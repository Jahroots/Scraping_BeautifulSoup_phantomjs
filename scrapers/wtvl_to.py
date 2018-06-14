# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class WtvlTo(SimpleScraperBase):
    BASE_URL = 'http://wtvl.to'

    def setup(self):

        raise NotImplementedError('Deprecated-Duplicate Scraper of WatchTvLinksSx.')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.long_parse = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/TVshows/' + self.util.quote(search_term) + '-page-1'

    def _fetch_no_results_text(self):
        return 'NO RESULTS !'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' › ')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.results-heading a'):
            #image = result.select_one('img')['src']
            soup = self.get_soup(self.BASE_URL + result['href'])
            videos = soup.select('#recent ul li a')

            for video in videos:
                self.submit_search_result(
                    link_url=self.BASE_URL + video['href'],
                    link_title=video['title']

                )

    @cacheable()
    def _extract_parse_info(self, link):
        # Note - this is caching
        # /Link/12345
        # Which is the same for both domains.  So when fetching
        # from one domain, we may reference the cache entry from this.
        soup = self.get_soup(self.BASE_URL + link)
        return {
            'index_page_title': self.util.get_page_title(soup),
            'link_url': soup.select_one('div.whatchbutton a')['href'],
        }

    def _parse_parse_page(self, soup):
        title = soup.select_one('#movie-title').text.strip()
        season, episode = self.util.extract_season_episode(soup.select_one('div.top-title strong').text)

        for link in soup.select('a[class="hostLink p2"]'):


            parse_info = self._extract_parse_info(link['href'])

            parse_info['link_title'] = title
            parse_info['series_season'] = season
            parse_info['series_episode'] = episode

            self.submit_parse_result(**parse_info)



class WatchTvLinksSx(WtvlTo):
    BASE_URL = 'http://watchtvlinks.sx'
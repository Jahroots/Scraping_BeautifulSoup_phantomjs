# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CacheableParseResultsMixin
from sandcrawler.scraper.caching import cacheable


class WatchTvLinksSx(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'http://wtvl.to'
    OTHER_URLS = ['http://watchtvlinks.sx',]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.long_parse = True

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/TVShows/' + self.util.quote(search_term) + \
               '-page-1'

    def _fetch_no_results_text(self):
        return 'NO RESULTS'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' › ')
        if link:
            self.log.debug('---------------------')
            return self.BASE_URL + link['href']

    def _extract_season_episode(self, text):
        srch = re.search('Season (\d+) Episode (\d+)', text)
        if srch:
            return srch.groups()
        return None, None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.results-heading a'):
            series_soup = self.get_soup(self.BASE_URL + result['href'])
            base_title = series_soup.find('div', {'id': 'movie-title'}).text
            for link in series_soup.select('div#recent li a'):
                season, episode = self._extract_season_episode(link.text)
                self.submit_search_result(
                    link_url=self.BASE_URL + link['href'],
                    link_title=base_title + ' ' + link.text,
                    series_season=season,
                    series_episode=episode,
                )


    @cacheable()
    def get_outlink(self, url):
        # note - this uses only the path, not the full domain,
        # so that way it will be cached for this, and other domains.
        link_soup = self.get_soup(self.BASE_URL + url)
        out_link = link_soup.select_one('.whatchbutton > a')
        if not out_link or not out_link.href:
            return None
        return out_link.href

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        fetched = set()
        for lnk in soup.select('.hostLink.p2'):
            if lnk.href in fetched:
                continue
            fetched.add(lnk.href)
            outlink = self.get_outlink(lnk.href)
            if not outlink:
                continue

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=outlink,
                link_title=lnk.text,
                )


class WtvlTo(WatchTvLinksSx):
    BASE_URL = 'http://wtvl.to'
    def setup(self):
        raise NotImplementedError('The WtvlTo and WatchTvLinksSx scrapers are the same')
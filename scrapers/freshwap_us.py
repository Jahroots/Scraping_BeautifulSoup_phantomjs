#coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import OpenSearchMixin, SimpleScraperBase

class FreshWapUs(OpenSearchMixin, SimpleScraperBase):

    BASE_URL = 'http://www.freshwap.us'
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    TERM = ''
    PAGE = 1
    COUNT = 0

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self._request_connect_timeout = 300
        self._request_response_timeout = 600
        self.bunch_size = 9
        self.showposts = 0
        self.media_type_to_category = 'film 32, tv 30'

    def _fetch_no_results_text(self):
        return  u'Unfortunately, site search yielded no results'

    def _fetch_search_url(self, search_term):
        return u'{}/'.format(self.BASE_URL)

    def _include_xy_in_search(self):
        return False

    # def _search_with_get(self):
    #     return True

    def _fetch_no_results_text(self):
        return 'site search yielded no results'

    def _parse_search_result_page(self, soup):
        for result in soup.find_all('div', 'meta'):
            self.submit_search_result(
                link_url=result.find_next('a', text=re.compile('Read More'))['href'],
                link_title=result.find_previous('div', 'title').text
            )


    def _parse_parse_page(self, soup):
        season= episode = None
        for link in soup.select('div.quote'):
            url = ''
            try:
                url = link.find('a')['href']
            except TypeError:
                pass
            if not url:
                url = link.find(text=re.compile('http'))
            title = soup.select_one('#news-title')
            if title:
                title = title.text
                season, episode = self.util.extract_season_episode(title)

            url = url.strip()
            if url.lower().endswith(('.com', '.net')):
                continue

            if season:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
            else:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_title=title,
                                         link_url=url
                                         )

class FreshWapOrg (FreshWapUs):
    BASE_URL = 'http://freshwap.org'

    def setup(self):
        raise NotImplementedError('Domain for sale.')

    def _do_search(self, start, r_from,):
        return self.post_soup(
            self.BASE_URL + '/index.php?do=search',
            data={
                    'do':'search',
                    'subaction':'search',
                    'search_start':start,
                    'full_search':0,
                    'result_from':r_from,
                    'story': self.search_term,
            },
            headers = {'X-Requested-With': 'XMLHttpRequest'}
        )

    def search(self, search_term, media_type, **extra):
        self.start = 1
        self.r_from = 0
        self.search_term = search_term
        soup = self._do_search(self.start, self.r_from)
        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        rslts = soup.select('div.main-title a')

        for result in rslts:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

        self.r_from = len(rslts)
        self.start += 1

        soup = self._do_search(self.start, self.r_from)
        self._parse_search_result_page(soup)


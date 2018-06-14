# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin

import json
class WatchmoviesPro(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.123movies.live'
    OTHER_URLS = ['http://www.movietvhub.com',
                  'http://watchmoviespro.me',
                  'http://www.watchmoviesall.com',
                  'http://www.watchmovies-pro.com',
                  'http://123movies.live'
                  ]
    SINGLE_RESULTS_PAGE = True


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self._request_connect_timeout = 300
        self._request_response_timeout = 600
        self._request_size_limit = (1024 * 1024 * 200)

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)


        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def get(self, url, **kwargs):
        return super(WatchmoviesPro, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/ajax/search.php', data = {'q' : search_term,
                                                                        'limit': '5',
                                                                        'timestamp' : '1490699942658',
                                                                        'verifiedCheck' : ''})

        text = soup.text.replace('</p></body></html>', '').replace('<html><body><p>', '')
        jo = json.loads(text)
        self.log.debug(jo)

        if not jo or len(jo) == 0:
            return self.submit_search_no_results()

        for result in jo:
            soup = self.get_soup(result['permalink'])

            a = soup.select_one('#mv-info a')

            if a:
                self.submit_search_result(
                    link_title=result['meta'],
                    link_url=a['href'],
                    image=result['image']
                )
            else:
                self.submit_search_result(
                    link_title=result['meta'],
                    link_url=result['permalink'],
                    image = result['image']
                )


    def _parse_search_result_page(self, soup):
        found = 0
        for link in soup.select('h5.left a.link'):
            found = 1
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )
        if not found:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.mvic-desc h3')
        if title and title.text:
            title = title.text

        series_season, series_episode = self.util.extract_season_episode(title)

        if soup.text.find('onclick="window.open(') > -1:
            url = soup.text.split('onclick="window.open(')[1].split(');')[0].replace('"','')

            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
        else:
            url = soup.text.split('<IFRAME')[1].split('allowfullscreen')[0].split('SRC=')[1].replace('"','')
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )


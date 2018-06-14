# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class GowatchseriesTo(SimpleScraperBase):
    BASE_URL = 'https://projecfreetv.co'
    OTHERS_URLS = ['https://theprojectfreetv.co', 'http://theprojectfreetv.co', 'https://gowatchseries.tv', 'http://gowatchseries1.to']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_AGENT_MOBILE = False
    USER_NAME = 'Hisseamed'
    PASSWORD = 'Fequao4abee'
    EMAIL = 'nelidarfriend@teleworm.us'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, ], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search-for-movies-tv-shows-or-people?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'No results found, please try on this website for tvshows'

    def _fetch_next_button(self, soup):
        return None

    def _login(self):
        soup = self.get_soup('https://projecfreetv.co/login')
        token = soup.select_one('input[name="_token"]')['value']
        self.log.debug(token)
        soup = self.post_soup(self.BASE_URL + '/sessions', data = {'username' : self.USER_NAME, 'password' : self.PASSWORD, '_token': token})

    def search(self, search_term, media_type, **extra):
        self._login()
        super(GowatchseriesTo, self).search(search_term, media_type, **extra)


    def _parse_search_result_page(self, soup):

        results = soup.select('figure[class*="figure"] a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for results in results:
            result = results['href']

            if 'movie' in result:
                title = results.text + ' ' + result
                season, episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=result,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )

            else:
                self.log.warning(result)
                ep_soup = self.get_soup(result)
                #self.log.debug(ep_soup)
                for ep_link in ep_soup.select('a[href*="seasons"]'):
                    title = results.text+' '+ ep_link.text
                    season, episode = self.util.extract_season_episode(title)
                    self.submit_search_result(
                        link_url=ep_link['href'],
                        link_title=title,
                        series_season=season,
                        series_episode=episode
                    )


    def _parse_parse_page(self, soup):

        title = soup.select_one('h1')
        if not title:
            title = soup.select_one('h2')

        if title:
            title = title.text.strip()

        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)

        iframe = soup.select_one('iframe.embed-responsive-item')
        if 'youtube' not in iframe['src']:
            self.log.warning(iframe['src'])
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                link_text=title,
                series_season=season,
                series_episode=episode
            )

        td = soup.select('table td[data-bind]')
        for t in td:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= self.util.find_urls_in_text(t['data-bind']).next(),
                link_text=title,
                series_season=season,
                series_episode=episode
            )

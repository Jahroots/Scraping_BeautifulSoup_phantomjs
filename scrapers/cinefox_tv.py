# coding=utf-8
import json
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase


class CineFoxTV(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'http://www.cinefox.tv'

    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = '2Yvy4BEz'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/search?q=%s' % self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(
                u'0 resultados encontrados') >= 0:
            return self.submit_search_no_results()

        for item in soup.select('.search-results-title'):
            title = item.text
            link = item.parent.href
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )

        next_button = soup.select('i.icono-pag-der')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    self.BASE_URL + next_button[0].parent['href'])
            )

    def get_page_cookies(self, parse_url):
        wd = self.webdriver()
        wd.get(parse_url)
        cookies_list = wd.get_cookies()
        cookies = []
        for cookie_list in cookies_list:
            if 'cinefox' in cookie_list['domain']:
                if 'cf_clearance' in cookie_list['name']:
                    cookies.append('cf_clearance=' + cookie_list['value'])
                elif '__cfduid' in cookie_list['name']:
                    cookies.append('__cfduid=' + cookie_list['value'])
                elif 'PHPSESSID' in cookie_list['name']:
                    cookies.append('PHPSESSID=' + cookie_list['value'])
        cookie = {'Cookie': '; '.join(cookies)}
        return cookie


    def parse(self, parse_url, **extra):

        if '/pelicula/' in parse_url:
            hdr = {
                'User-Agent': self._get_http_user_agent(),
                'Referer': parse_url, 'X-Requested-With': 'XMLHttpRequest'}
            cookie = self.get_page_cookies(parse_url)
            soup=self.get_soup(parse_url)
            index_page_title = self.util.get_page_title(soup)
            data_media = json.loads(soup.select_one('div.trigger-trailer')['data-media'])
            idm = data_media['idm']
            mediaType = data_media['mediaType']
            pelicula_soup = self.make_soup(json.loads(self.get('http://www.cinefox.tv/media/partials?idm={}&mediaType={}'.format(idm, mediaType), headers=hdr, cookies=cookie).text)['sources'])
            data_sources = pelicula_soup.select('div.available-source')
            for data_source in data_sources:
                link = data_source['data-url']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_text=link,
                )
        if '/serie/' in parse_url:
            serie_soup = self.get_soup(parse_url + '/episodios?fragment=true&ajax=true')
            idms_data = serie_soup.find_all('div', "ep-list-report")
            for idm_data in idms_data:
                referer_link = idm_data.find_previous('a')['href']
                title = self.get_soup(referer_link).select_one('meta[property="og:title"]')['content']
                index_page_title = self.util.get_page_title(self.get_soup(referer_link))
                series_season = series_episode = None
                if title:
                    series_season, series_episode = self.util.extract_season_episode(
                        title)
                data_report = json.loads(idm_data.find('i', 'icondarze-spoiler report-tooltip-icon')['data-report'])
                idm = data_report['idm']
                media_type = data_report['mediaType']
                episode_idm = data_report['episodeIdm']
                hdr = {
                    'User-Agent': self._get_http_user_agent(),
                    'Referer': parse_url, 'X-Requested-With': 'XMLHttpRequest'}
                cookie = self.get_page_cookies(parse_url)
                episode_links_soup = self.make_soup(json.loads(self.get('http://www.cinefox.tv/media/partials?idm={}&episodeIdm={}&mediaType={}'.format(idm, episode_idm, media_type), headers=hdr, cookies=cookie).text)['sources'])
                data_sources = episode_links_soup.select('div.available-source')
                for data_source in data_sources:
                    link = data_source['data-url']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_text=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

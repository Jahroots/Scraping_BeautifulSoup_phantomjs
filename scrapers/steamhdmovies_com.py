# coding=utf-8
import json
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SteamhdmoviesCom(SimpleScraperBase):
    BASE_URL = 'http://steamhdmovies.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/cari?cari={search_term}&id={page}/'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return u"couldn't find what you want"

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.box'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('b.judul')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        id_item = soup._url.split('/')[-1].split('-')[0]
        data={'host':'steamhdmovies.com', 'ref':'steamhdmovies.com', 'idItem': id_item}
        token_soup = self.post_soup('http://steamhdmovies.com/generateToken', data=data)
        token = json.loads(token_soup.text)['data']['token']
        key_id = soup.select_one('meta[name="watchdojo-embed"]')
        if key_id:
            key_id = key_id['data-key']
            prime_link = json.loads(self.get_soup('http://steamhdmovies.com/embed/{}/?key={}&host=steamhdmovies.com&token={}'
                                                  .format(id_item, key_id, token)).text)['data']['video']['ihik2']
            source = self.get(prime_link).text
            links_list = re.findall('source src="(.*?)"', source)
            for link in links_list:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        download_soup = self.get_soup(soup._url.replace('/watch/', '/download/'),  allowed_errors_codes=[404])
        er_title = download_soup.select_one('h1')
        if er_title:
            er_title = er_title.text
            if '404' not in er_title:
                for link in download_soup.select('div#box-movie select option')[1:-1]:
                    movie_link = self.get_redirect_location(self.BASE_URL+'/download/s/'+link['value'])
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=movie_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

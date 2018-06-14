# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import re

class FptplayNet(SimpleScraperBase):
    BASE_URL = 'https://fptplay.vn'
    OTHER_URLS = ['https://fptplay.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def _fetch_search_url(self, search_term, media_type):
        self.search_term = search_term
        return '{base_url}/tim-kiem/{search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Không có kết quả tìm kiếm cho từ khóa'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        has_results = self._parse_search_result_page(soup)


        page = 2
        while self.can_fetch_next() and has_results:
            soup = self.post_soup(
                '{}/show/more'.format(self.BASE_URL),
                data = {
                    'type':'search',
                    'stucture_id':'search',
                    'page': page,
                    'keyword': self.search_term
                }
            )

            has_results = self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        has_results = False
        for result in soup.select('div.list_img'):
            has_results = True
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
        return has_results

    @cacheable()
    def _extract_url(self, id, episode, referer):
        response =  self.post(
            '{}/show/getlink'.format(self.BASE_URL),
            data = {
                'id': id,
                'type':'newchannel',
                'quality': 3,
                'episode': episode,
                'mobile': 'web',
            },
            headers = {
                'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
            }
        ).json()
        return (response['stream'], response['name'])

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('a.player_title_name')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        # Dig out id = 'xxx'
        for id in re.findall("var id = '(.*?)'", unicode(soup)):
            episode_soup = self.post_soup(
                '{}/show/episode'.format(self.BASE_URL),
                data={
                    'page':1,
                    'film_id': id,
                },
                headers = {
                    'Referer': soup._url,
                    'X-Requested-With': 'XMLHttpRequest',
                }
            )
            for episode_li in episode_soup.select('li.episode_image_item'):
                episode = episode_li.get('rol')
                if episode:
                    url, name = self._extract_url(id, episode, soup._url)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=name,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

# coding=utf-8
import json
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class FilmstreamitaCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://beststreaming.info'
    OTHER_URLS = ['http://filmstreamita.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('the website is offline')
        super(FilmstreamitaCom, self).setup()
        self._request_connect_timeout = 900
        self._request_response_timeout = 900

    def _fetch_no_results_text(self):
        return u'Purtroppo la ricerca non ha prodotto risultati'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.news2'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.lf a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        film_id = soup.select_one('a#hdstream_text')['href'].split('id=')[-1]
        for link_value in soup.select('select#sseriesSeries option'):
            data = {'news_id':film_id, 'series':link_value['value']}
            series_page = self.post('http://filmstreamita.com/engine/ajax/a.sseries.php', data=data)
            json_status = json.loads(series_page.text)['status']
            if json_status == 0:
                continue
            json_series_soup = self.make_soup(json.loads(series_page.text)['links'])
            for link in json_series_soup.select('div.lf a'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )


# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WebteizleOrg(SimpleScraperBase):
    BASE_URL = 'http://webteizle.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/ajax/autocompletesearch.asp?q={search_term}&limit=100'.format(base_url=self.BASE_URL,
                                                                                         search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Hiçbir Şey Bulunamadı'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results_json = json.loads(soup.text)
        if u'afis/yok.jpg' in results_json[0]['afis']:
            return self.submit_search_no_results()
        else:
            for result_json in results_json:
                image = self.BASE_URL+result_json['afis']
                link = self.BASE_URL+result_json['url']
                link_title = self.BASE_URL+result_json['filmadi']
                self.submit_search_result(
                    link_url=link,
                    link_title=link_title,
                    image=image,
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div#woca-pagination a'):
            link = result.href
            pagination_soup = self.get_soup(link)
            link_id = player_class = None
            try:
                link_id = pagination_soup.select_one('div#kendisi script').text
            except AttributeError:
                player_class = pagination_soup.select_one('div#kendisi div')['class'][0]
            if link_id:
                if 'movshare' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'http://embed.movshare.eu/embed.php?v='+movie_link_id
                elif 'divxstage' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'http://www.cloudtime.to/embed/?v='+movie_link_id
                elif 'mailru' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'http://webteizle.org/player/video-mail-ru.asp?v='+movie_link_id
                elif 'okru' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'http://webteizle.org/player/ok.ru.asp?v='+movie_link_id
                elif 'openload' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'https://oload.tv/embed/'+movie_link_id
                elif 'uptobox' in link_id:
                    movie_link_id = link_id.split("',")[0].split("('")[-1]
                    movie_link = 'http://uptobox.com/'+movie_link_id
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=result.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
            if player_class:
                if 'plusplayer' in player_class:
                    movie_link = 'http://webteizle.org/player/plusplayer.asp?v='+pagination_soup.select_one('div#kendisi div').text
                elif 'plusplayer2' in player_class:
                    movie_link = 'http://webteizle.org/player/plusplayer.asp?v=' + pagination_soup.select_one(
                        'div#kendisi div').text
                elif 'plusplayerV2' in player_class:
                    movie_link = 'http://720pizle.com/player/plusplayer2.asp?v=' + pagination_soup.select_one(
                        'div#kendisi div').text
                elif 'plusplayer2V2' in player_class:
                    movie_link = 'http://720pizle.com/player/plusplayer2.asp?v=' + pagination_soup.select_one(
                        'div#kendisi div').text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=result.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

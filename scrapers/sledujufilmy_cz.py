# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SledujufilmyCz(SimpleScraperBase):
    BASE_URL = 'https://sledujufilmy.cz'
    OTHER_URLS = ['http://serialy.sledujufilmy.cz',]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_NAME = 'Carsed1945'
    PASSWORD = 'cah3woo2Ee'
    EMAIL = 'josephjyuan@dayrep.com'

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/vyhledavani/?search={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text='Další »')
        return self.BASE_URL+next_link['href'] if next_link else None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404,], **kwargs)

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('div.mlist--list div.info'):
            if 'porady.' in result.find('a')['href']:
                continue
            title = result.find_next('h3').text
            self.submit_search_result(
                link_url=result.find('a')['href'],
                link_title=title
            )
            any_results = True
        for result in soup.select('div.movies_list a.item'):
            if 'trailery.' in result['href'] or 'herci.' in result['href']:
                continue
            episode_soup = self.get_soup(result['href'] )
            for episode_links in episode_soup.select('ul.episodes li a.view'):
                title = episode_soup.find('h2', 'first').text.strip()
                self.submit_search_result(
                    link_url=episode_links['href'],
                    link_title=title
                )
                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        class_link = soup.find('div', id='play_block')
        if class_link:
            class_link = class_link.find('a')
            class_name = class_link['class'][0]

            if 'play-movie' in class_name or 'play-movie-v2' in class_name:
                title = soup.find('div', 'names').find('strong').text.strip()
                movie_link_soup = self.get_soup('http://stream-a-ams1xx2sfcdnvideo5269.cz/okno.php?movie={}&new_way'.format(class_link['data-loc']))
                for result in movie_link_soup.select('div.player-container iframe'):
                    movie_link = ''
                    try:
                        movie_link = result['src']
                    except KeyError:
                        pass
                    if movie_link:
                        self.submit_parse_result(
                                            index_page_title=index_page_title,
                                            link_url=movie_link,
                                            link_title=title,
                                        )


        if 'serialy' in soup._url:
            title = soup.find('h2', 'first').find('span').text.strip()
            links = soup.select('#episodes--list ul.episodes a[class="view play-epizode-direct"]')
            for link in links:
                data_loc = link['data-loc']
                movie_link_soup = self.get_soup(
                    'http://stream-a-ams1xx2sfcdnvideo5269.cz/prehravac.php?play=serail&id={}'.format(
                        data_loc))
                for result in movie_link_soup.select('iframe'):
                    movie_link = ''
                    try:
                        movie_link = result['src']
                    except KeyError:
                        pass
                    season, episode = self.util.extract_season_episode(soup._url)
                    if movie_link:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=movie_link,
                            link_title=title,
                            series_season=season,
                            series_episode=episode
                        )



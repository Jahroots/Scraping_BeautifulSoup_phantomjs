# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class FilmyhdNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://filmyhd.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_NAME = 'Hoppenced'
    PASSWORD = 'aiyuaFu8ooz'
    EMAIL = 'RandyTWatson@rhyta.com'


    def _fetch_no_results_text(self):
        return u'Wyszukiwanie nie zwróciło żadnych wyników'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Następna')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        # Login
        soup = self.post_soup(self.BASE_URL, data={'login_name': self.USER_NAME,
                                                   'login_password': self.PASSWORD,
                                                   'login': 'submit'
                                                   }
                              )
        self.log.debug(soup.select_one('#menu_right #item').text)
        super(self.__class__, self).search(search_term, media_type, **extra)


    def _parse_search_result_page(self, soup):
        flag = 0
        for result in soup.select('div#dle-content table[align="center"] td[colspan="4"]'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            flag = 1
        if not flag:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        self.post_soup(self.BASE_URL, data={'login_name': self.USER_NAME,
                                                   'login_password': self.PASSWORD,
                                                   'login': 'submit'
                                                   }
                              )
        soup = self.get_soup(soup._url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        links = self.util.find_urls_in_text(soup.select_one('#text').text)
        for link in links:
            if 'youtu' not in link:
                videos = link.split('http')
                for video in videos:
                    if video:
                        self.log.debug(video)
                        self.submit_parse_result(
                            index_page_title = index_page_title,
                            link_url = 'http' + video,
                            link_title = title,
                            series_season = series_season,
                            series_episode = series_episode
                        )

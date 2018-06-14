# coding=utf-8
#
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class QuedustreamCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.quedustreaming.com'
    OTHER_URLS = ['http://www.quedustream.com',]

    SEARCH_FILM_URL = '/rechercher-un-film.html'
    SEARCH_SERIE_URL = '/rechercher-une-serie.html'
    SEARCH_MANGA_URL = '/rechercher-un-manga.html'

    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'winter'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'
        super(self.__class__, self).setup()

    def _fetch_search_url(self, search_term, media_type):

        if media_type == ScraperBase.MEDIA_TYPE_FILM:
            return self.BASE_URL + self.SEARCH_FILM_URL
        elif media_type == ScraperBase.MEDIA_TYPE_TV:
            return self.BASE_URL + self.SEARCH_SERIE_URL
        else:
            return self.BASE_URL + self.SEARCH_MANGA_URL

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None


    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        soup = ''
        if media_type == ScraperBase.MEDIA_TYPE_FILM:
            soup = self.post_soup(search_url, data={'searchf': search_term})
        elif media_type == ScraperBase.MEDIA_TYPE_TV:
            soup = self.post_soup(search_url, data={'searchs': search_term})
        else:
            soup = self.post_soup(search_url, data={'searchm': search_term})

        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('td div a.b')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('td div'):
            link = result.select_one('a.b')
            if 'voir-serie' in link.href:
                soup = self.get_soup(self.BASE_URL + '/' + link.href)
                seasons = soup.select('div.tggm a.e')
                for season in seasons:
                    self.submit_search_result(
                        link_url=self.BASE_URL + '/' + season.href,
                        link_title=season.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('span.lien_video a.b'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        for e in soup.select('div.saison a.e'):
            soup = self.get_soup(self.BASE_URL + '/' + e.href)
            for link in soup.select('span.lien_video a.b'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for a in soup.select('div.liste_episodes table a'):
            soup = self.get_soup(self.BASE_URL + '/' + a.href)
            for link in soup.select('a[href*="http://www.protect-stream.com"]'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )


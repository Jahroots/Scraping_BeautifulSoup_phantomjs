# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin, \
    ScraperParseException
from sandcrawler.scraper.caching import cacheable


class QuikrmoviesTo(SimpleScraperBase, AntiCaptchaMixin):
    BASE_URL = 'https://quikrmovies.to'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    RECAPKEY = '6LeURiITAAAAAKgZXhLvV36s4XDJu8IVz2x7CC6O'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/{search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'NO RESULT FOUND'

    def get_recap_soup(self, url):
        soup = self.post_soup(
            url,
            data={'g-recaptcha-response': self.get_recaptcha_token()}
        )
        return soup


    def search(self, search_term, media_type, **extra):
        """
        Throws up a recaptcha on search; submit and continue

        Does not search if the search term has spaces! Balls.
        """
        search_term = search_term.replace(' ', '')
        search_url = self._fetch_search_url(search_term, media_type)
        response = self.get(search_url, allowed_errors_codes=[404, ])
        self.base_search_url = response.url
        if response.status_code == 404 and 'recaptcha' in response.content:
             soup = self.get_recap_soup(response.url)
        else:
            soup = self.make_soup(response.content)
        self._parse_search_results(soup)

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[rel="next"]')
        if next_button:
            return self.base_search_url + next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('li.movie-list-item'):
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
        for iframe in soup.select('iframe'):
            src = iframe.get('src', iframe.get('data-src', None))
            if not src:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                series_season=series_season,
                series_episode=series_episode,
            )

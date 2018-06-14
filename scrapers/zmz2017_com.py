# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json

class Zmz2017Com(SimpleScraperBase):
    BASE_URL = 'http://www.zimuzu.tv'
    OTHER_URLS = ['http://xiazai002.com', 'http://www.zmz2017.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP,]
    LANGUAGE = 'zho'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    PAGE = 1
    URL = BASE_URL + '/search/index?page={}&keyword={}&search_type='
    TERM = ''

    def _fetch_search_url(self, search_term, media_type):
        self.TERM = search_term
        return self.BASE_URL + '/search/index?page={}&keyword={}&search_type='.format(self.PAGE, search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        next_button = self.URL.format(self.PAGE, self.TERM)
        return  next_button

    def search(self, search_term, media_type, **extra):
        self.PAGE = 1
        soup = self.get_soup(self._fetch_search_url(search_term, media_type))

        results = soup.select('div[class="clearfix search-item"]')

        if not results or len(results) == 0:
            self.PAGE = -1
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        if self.PAGE != -1 and self.can_fetch_next():
            next_button = self._fetch_next_button(soup)
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        results = soup.select('div[class="clearfix search-item"]')

        for result in results:
            link = result.select_one('a')

            soup = self.get_soup(self.BASE_URL + link.href)
            link = soup.select_one('p a.f3')
            if link.href.find('torrent') > -1:
                continue
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div[class="tc title"]')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        text = soup.text.split('file_list=')[1].split('}}')[0].strip() + '}}'
        data = json.loads(text)

        for key, value in data.iteritems():
            for k, v in value.iteritems():
                url = v
                if url.find('torrent') > -1:
                    continue

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )


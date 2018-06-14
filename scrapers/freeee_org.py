# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FreeeeOrg(SimpleScraperBase):
    BASE_URL = 'http://www.freeee.org'
    OTHER_URLS = ['http://yysr3sj2.freeee.org']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated, website just show ads.')

    def _fetch_search_url(self, search_term, media_type):
        return 'http://yysr3sj2.freeee.org/getSearch/1/{search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('ul', 'pagination').find_all('a')[-1]
        if next_button:
            return 'http://yysr3sj2.freeee.org/getSearch/'+'/'.join(next_button.href.split('/')[-2:])
        return None

    def _parse_search_results(self, soup):
        if '0-free-online-' in soup.select_one('div.product-thumb a').href.split('?/')[-1]:
             return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.product-thumb'):
            link = self.OTHER_URLS[0]+'/getMovie/'+result.select_one('a').href.split('?/')[-1]
            self.submit_search_result(
                link_url=link,
                link_title=link,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('td.table-middle a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        for result in soup.select('tr[itemprop="episode"]'):
            link = self.OTHER_URLS[0]+'/getMovie/'+result.select_one('a').href.split('?/')[-1]
            movie_soup = self.get_soup(link)
            for movie_link in movie_soup.select('td.table-middle a'):
                self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link.href,
                        link_title=movie_link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

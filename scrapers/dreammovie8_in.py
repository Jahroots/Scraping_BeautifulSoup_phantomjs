# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Dreammovie8In(SimpleScraperBase):
    BASE_URL = 'http://dreammovie.eu'
    OTHER_URLS = ['http://dreammovie8.in']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'wCCza2GK'


    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/search/stories-search/'.format(base_url=self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def search(self, search_term, media_type, **extra):
        url =  self._fetch_search_url(search_term, media_type)
        soup = self.post_soup(url , data = {'query' : search_term,
                                            'topic' : '',
                                            'contenttopic' : '',
                                            'author' : '',
                                            'comments_pos' : 'News',
                                            'days' : 0,
                                            'op' : 'stories_search'})
        self._parse_search_results(soup)


    def _parse_search_results(self, soup):
        results = soup.select('div.OpenTableContent img[src="images/folders.gif"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1

        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_result_page(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.OpenTableContent img[src="images/folders.gif"]'):
            link = result.find_next('font', 'option').select_one('a')
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
        for link in soup.select('div.Content p a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmeSerialeHdCom(SimpleScraperBase):
    BASE_URL = 'http://www.filme-seriale-hd.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    PAGE = 1

    def setup(self):
        raise NotImplementedError("The website is out of reach")

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Nu există nicio postare care să corespundă interogării'

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        next_button = self.BASE_URL + '/search?updated-max=2017-03-19T09%3A32%3A00%2B02%3A00&max-results=18#PageNo={}'.format(str(self.PAGE))
        return next_button


    def _parse_search_result_page(self, soup):
        for result in soup.select('#Blog1 div[class="post hentry"]'):
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
        for link in soup.select('div.blog-posts iframe'):
            mov_link = link['src']
            mov_text = link.text
            if mov_link:
                if 'http' not in mov_link:
                    mov_link = 'http:'+mov_link
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=mov_link,
                    link_title=mov_text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

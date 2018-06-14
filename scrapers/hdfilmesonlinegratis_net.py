# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HdfilmesonlinegratisNet(SimpleScraperBase):
    BASE_URL = 'http://filmesonlinegratisahd.com'
    OTHER_URLS = ['http://hdfilmesonlinegratis.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    page = 1
    search_term  = ''

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Conteúdo atualmente indisponível'

    def _fetch_next_button(self, soup):
        self.page += 1
        return self.BASE_URL + '/page/' + str(self.page) +'/?s=' + self.util.quote(self.search_term)

    def search(self, search_term, media_type, **extra):
        self.page = 1
        self.search_term = search_term

        super(self.__class__, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.data h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        #Online in site
        for link in soup.select('#player2 iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class YaskeMobi(SimpleScraperBase):
    BASE_URL = 'http://yaske.mobi'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    ALLOW_FETCH_EXCEPTIONS = True

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No results to show'

    def _fetch_next_button(self, soup):
        icon_caret = soup.select_one('i.icon-caret-right')
        if icon_caret:
            return icon_caret.parent.href
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        results = soup.select('div.result-item a')
        if results:
            for result in soup.select('div.result-item'):
                link = result.select_one('a')
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
                found = 1
        else:
            for result in soup.select('#serie_contenido ul.episodios'):
                link = result.select_one('a')
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
                found = 1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('iframe[class="metaframe rptss"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

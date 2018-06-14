# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin, DuckDuckGo

class SmotrimSerialCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://smotrim-serial.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]



    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов. Попробуйте изменить или сократить Ваш запрос.	'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('Поиск по сайту')
        if next_button:
            return next_button.href
        return None

    """
    This scraper is not working well. The website has an unformatted template such as
            #{search-id}: [result-link]{result-title}[/result-link]
    """

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.story_info span.info_cat'):
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
        for link in soup.select('dfsafaf'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

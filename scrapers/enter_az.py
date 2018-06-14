# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class EnterAz(SimpleScraperBase):
    BASE_URL = 'http://enter.az'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?query=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал результатов.Попробуйте изменить или сократить Ваш запрос'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>>')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class*="poster"] a')

        for result in results:
            link = result
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

        for link in soup.select('object param[name="flashvars"]'):
            src = link['value'].split('src=')[1].split('%22')[1]
            if src:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase


class Hd720Biz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://hd720.biz'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.bunch_size = 16
        self.showposts = 1


    def get(self, url, **kwargs):
        return super(Hd720Biz, self).get(url, **kwargs)

    def post(self, url, **kwargs):
        return super(Hd720Biz, self).post(url, **kwargs)

    def _fetch_no_results_text(self):
        return u'поиск по сайту не дал никаких результатов'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('div.shortstory-film a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(soup._url)
        for link in soup.select('select#series option'):
             self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['value'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
        for link in soup.select('div#ts3 iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )

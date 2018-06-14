# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class FindTV(SimpleScraperBase):
    BASE_URL = 'http://findtv.net'
    SINGLE_RESULTS_PAGE = True

    def setup(self):

        # raise NotImplementedError('Required paid subsdcription')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "eng"

        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return

    def _login(self):
        soup = self.get_soup(self.BASE_URL + '/login.php')
        token = soup.find('input', type="hidden", value="login")['name']
        token_fields = soup.find('input', dict(type="hidden",
                                               name="data[_Token][fields]"))[
            'value']  # ="0f427d2a32eb2e08c7e74b10970b12e2beff0237%3A" id="TokenFields1744407364")['name']

        self.post(self.BASE_URL + '/reg.php', data={
            '_method': 'POST',
            # 'Token1935871008'
            token: 'login',
            'UserUsername': 'sands8',
            'subscriptionsPass': 'crawl8',
            'data[_Token][fields]': '0f427d2a32eb2e08c7e74b10970b12e2beff0237%3A',
        })

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/searchlist.php', data=dict(q=search_term))
        self._parse_search_results(soup)

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        # No 'no results' message - just check for a lack of reslts.
        results = soup.select('.index_main-right-lb li a')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        self._login()
        index_page_title = self.util.get_page_title(soup)
        for serie_link in soup.find('div','detailed_main-left-Season-list').find_all('li'):
            if serie_link.find('em'):
                serie_video_url = self.BASE_URL + serie_link.find('a')['href']
                title = serie_link.text
                season, episode = self.util.extract_season_episode(title)
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=serie_video_url,
                                         link_title=title,
                                         series_season = season,
                                         series_episode = episode
                                         )

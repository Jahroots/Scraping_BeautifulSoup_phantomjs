# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class LuckyworldNet(SimpleScraperBase):
    BASE_URL = 'http://www.luckyworld.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'kor'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('The website became a paid resource')


    def _fetch_search_url(self, search_term, media_type=None, start=0):
        self.start = start
        self.search_term = search_term
        return '{base_url}/disk/board.php?board=1&listmode=all&sf=subject&sw={search_term}&page={page}/'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return None

    def _parse_search_results(self, soup):
        if soup.select('div.noSearchResult'):
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('span.fullSubject'):
            link = result.select_one('a')['onclick'].split("('")[-1].split("'")[0]
            self.submit_search_result(
                link_url=link,
                link_title=result.select_one('a').text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('b.judul')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        links = None
        try:
            links = self.util.find_urls_in_text(soup.select_one('div#player_1').find_next('script').text)
        except AttributeError:
            pass
        if links:
            for link in links:
                if '/image/' in link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
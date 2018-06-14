# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class BeetvMe(SimpleScraperBase):
    BASE_URL = 'http://myputlocker.me'
    OTHER_URLS = ['http://beetv.to', 'http://beetv.me']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'qa5h7yMK'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, no results were found'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('span.eplink a'):
            ep_soup = self.get_soup(results['href'])
            title = ep_soup.select_one('h1').text.strip()
            for ep_links in ep_soup.select('div.episodes-list-wrapper ul.collapse a'):
                ep_link = ep_links['href']
                series_season, series_episode = self.util.extract_season_episode(ep_link)
                self.submit_search_result(
                    link_url=ep_link,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(title)
        for results in soup.select('div.postTabs_divs iframe'):
            movie_link = results['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class LakornhitCom(SimpleScraperBase):
    BASE_URL = 'http://www.lakornhit.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tha'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/result?keyword={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('td.info-cate a'):
            result = results['href']
            ep_soup = self.get_soup(result)
            for ep_links in ep_soup.select('ul.thumbnails p.video-title a'):
                title = ep_links.text.strip()
                series_season, series_episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=ep_links['href'],
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
                found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.player iframe')
        for result in results:
            movie_link = result['src']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )
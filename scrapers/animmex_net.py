# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class AnimmexNet(SimpleScraperBase):
    BASE_URL = 'https://www.animmex.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'

    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Website Not Available')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/videos?search_query={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No Videos Found'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.col-md-9 a'):
            if 'search_query' in results['href']:
                continue
            title = results.find('span', 'video-title').text.strip()

            series_season, series_episode = self.util.extract_season_episode(title)
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
                series_season=series_season,
                series_episode=series_episode,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3').text.strip()
        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(title)
        for results in soup.select('div.video-container iframe'):
            movie_soup = self.get_soup(results['src'])
            movie_link = movie_soup.find('video').find_next('source')['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )
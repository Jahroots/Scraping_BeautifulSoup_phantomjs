# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SerieswNet(SimpleScraperBase):
    BASE_URL = 'http://www.seriesw.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No Clips Found For'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h1 a'):
            url = results['href']
            if 'http' not in url:
                url = self.BASE_URL + url
            ep_soup = self.get_soup(url)
            for ep_links in ep_soup.select('a.lcc'):
                title = ep_links.text.strip()
                series_season, series_episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=ep_links['href'],
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
        for results in soup.select('div.tab_container div iframe')+soup.select('div.subtab_container div iframe'):
            try:
                movie_link = results['src']
            except KeyError:
                movie_link = results['data-src']
            if '/script/' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )
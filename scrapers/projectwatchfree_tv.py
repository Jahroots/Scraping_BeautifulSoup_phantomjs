# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class ProjectwatchfreeTv(SimpleScraperBase):
    BASE_URL = 'http://project-free-tv.ag'
    OTHER_URLS = ['http://project-free-tv.li', 'http://projectwatchfree.tv']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Duplicate of ProjectFreeTV')

    def _fetch_search_url(self, search_term, media_type):
        if media_type == ScraperBase.MEDIA_TYPE_FILM:
            return self.BASE_URL + '/movies/search-form/?free={}'.format(self.util.quote(search_term))
        else:
            return self.BASE_URL + '/search-tvshows/?free={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No results found'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        has = 0
        results = soup.select('table.alternate_color a')
        if results:
            for results in results:
                ep_soup = self.get_soup(self.BASE_URL + results['href'])
                for episode_links in ep_soup.select('table.alternate_color th div'):
                    title = episode_links.text
                    season, episode = self.util.extract_season_episode(title)
                    link = episode_links.select_one('a')
                    has = 1
                    self.submit_search_result(
                        link_url=link['href'],
                        link_title=title,
                        series_season=season,
                        series_episode=episode
                  )
        else:
            #movies
            results = soup.select('div.hfeed div a')
            for links in results:
                title = links.text
                season, episode = self.util.extract_season_episode(title)
                has = 1
                self.submit_search_result(
                    link_url=links['href'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode,
                    image = self.util.find_image_src_or_none(links, 'img')
                )
        if has == 0:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1')

        if not title:
            title = soup.select_one('div.single_post b')

        if title and title.text:
            title = title.text

        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in soup.select('table[class="alternate_color variousfont"] tr'):
            url = link.select_one('a')
            if url:
                url = url['href']
                if url.find('http') == -1:
                    url = self.BASE_URL + url

                soup = self.get_soup(url)
                iframe = soup.select_one('iframe[allowfullscreen]')
                if iframe:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url= iframe['src'],
                        series_season=season,
                        series_episode=episode,
                        link_text=title,
                    )
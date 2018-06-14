# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class CinemavfBiz(SimpleScraperBase):
    BASE_URL = 'http://filmstreamin.cc'
    OTHER_URLS = ['http://filmstreamin.ws', 'http://filmstreamin.net', 'http://filmstreamin.com', 'http://cinemavf.tv', 'http://cinemavf.info', 'http://cinemavf.ws', 'http://cinemavf.biz', 'http://cinemavf.cc', 'http://cinemavf.bz']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def search(self, search_term, media_type, **extra):
            search_soup = self.get_soup(
                self.BASE_URL+'/?s={}'.format(self.util.quote(search_term)))
            self._parse_search_results(search_soup)

    def _parse_search_results(self, soup):
            found = 0
            for link in soup.select('h2.entry-title a')+soup.select('div.entry-title a'):
                if '/serie/' in link.href:
                    series_soup = self.get_soup(link.href)
                    for episode_link in series_soup.select('a.num_episode'):
                        episode_title = episode_link.text
                        series_season, series_episode = self.util.extract_season_episode(episode_title)
                        self.submit_search_result(
                            link_url=episode_link.href,
                            series_season=series_season,
                            series_episode=series_episode,
                            link_title=episode_title,
                        )
                else:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                    )
                found = 1
            if not found:
                return self.submit_search_no_results()
            next_link = soup.find('a', text='»')
            if next_link and self.can_fetch_next():
                self._parse_search_results(self.get_soup(
                   next_link['href']
                ))

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(index_page_title)
        for other_links in soup.select('div.links-container ul li'):
            levideo_id = other_links.find('input')['value']
            data = {'levideo': levideo_id}
            iframe_soup = self.post_soup(page_url, data=data)
            iframe_link = iframe_soup.select_one('div#player iframe')['src']
            if 'http' not in iframe_link:
                iframe_link = 'http:' + iframe_link
            self.submit_parse_result(
                link_url=iframe_link,
                index_page_title=index_page_title,
                series_season=series_season,
                series_episode=series_episode,
            )
        iframe_link = ''
        try:
            iframe_link = soup.select_one('div#player iframe')['src']
        except TypeError:
            pass
        if iframe_link:
            self.submit_parse_result(
                link_url=iframe_link,
                index_page_title=index_page_title,
                series_season=series_season,
                series_episode=series_episode,
            )
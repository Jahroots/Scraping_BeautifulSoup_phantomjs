# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class WatchseriesGoTo(SimpleScraperBase):
    BASE_URL = 'https://www.watchseries.ac'
    OTHER_URLS = ['http://www.watchseriesgo.to', 'https://www.watchseriesgo.to']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    LONG_PARSE = True

    def setup(self):
        raise NotImplementedError('the website is out of reach')

    def _fetch_no_results_text(self):
        return u'is not found in our database'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        blocks = soup.find_all('div', 'block-left-home-inside-text')
        for block in blocks:
            link = block.find('a')['href']
            episode_soup = self.get_soup(self.BASE_URL + link)
            for row in episode_soup.find_all('tr', itemprop='episode'):
                episode_link = row.find('a', 'table-link')
                self.submit_search_result(
                    link_url=self.BASE_URL + episode_link.href,
                    link_title=episode_link.text.strip(),
                )

    @cacheable()
    def _get_link_destination(self, link):
        soup = self.get_soup(self.BASE_URL + link)
        try:
            return soup.find('div', id='video-embed').find('iframe')['src']
        except TypeError:
            return soup.find('div', id='video-embed').find('a')['href']

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)

        for episode_link in soup \
                .find('table', 'table table-hover table-links') \
                .select('a.buttonlink'):
            link = self._get_link_destination(episode_link['href'])
            self.submit_parse_result(
                index_page_title=index_page_title,
                series_season=season,
                series_episode=episode,
                link_url=link,
                link_title=episode_link.text
            )
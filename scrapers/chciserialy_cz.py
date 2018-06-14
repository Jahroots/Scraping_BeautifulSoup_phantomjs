# coding=utf-8
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CacheableParseResultsMixin


class ChciserialyCz(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.chciserialy.cz'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True

    def _fetch_no_results_text(self):
        return u'Nebylo nic nalezeno'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/vyhledavac/index/{}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def parse_series(self, parse_url):
        soup = self.get_soup(parse_url)
        panels = soup.find('div', 'seasons').find_all('ul')
        for panel in panels:
            for links in panel.find_all('a'):
                link, name = links['href'], links.text
                yield self.BASE_URL+'/'+link, name

    def _parse_search_result_page(self, soup):
        for series_link in soup.select('div.series-info div.series-name a'):
            if '/serie/' in series_link['href']:
                se_links = self.parse_series(self.BASE_URL+'/'+series_link['href'])
                for se_link in se_links:
                    link, name = se_link
                    self.submit_search_result(
                            link_url=link,
                            link_title=name,
                        )
            else:
                link=series_link['href']
                name=series_link.text
                self.submit_search_result(
                    link_url=link,
                    link_title=name,
                )

    def _parse_parse_page(self, soup):
        video_links = soup.select('.video a')
        season_text = soup.find('section', 'prehratdil').find('header').find('p').text.strip()
        season = re.search(u'Série:\s+\d{2}', season_text).group().split()[-1]
        episode = re.search(u'Epizoda:\s+\d{2}', season_text).group().split()[-1]
        for video_link in video_links:
            title = self.util.get_page_title(soup)
            episode_soup = self.get_soup(video_link['href'])
            url = episode_soup.find('div', 'video')
            if url and url.iframe and url.iframe.has_attr('src'):
                url = url.iframe['src']
                self.submit_parse_result(
                    index_page_title=title,
                    series_season=season,
                    series_episode=episode,
                    link_url=url
                )

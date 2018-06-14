# -*- coding: utf-8 -*-
import base64
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase
from sandcrawler.scraper.testrig import TestRig

class TainiesOnline(CloudFlareDDOSProtectionMixin, SimpleScraperBase, TestRig):
    BASE_URL = 'https://tainies.online'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'gre'

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        self.webdriver().get(search_url)
        soup = self.make_soup(self.webdriver().page_source)
        self._parse_search_results(soup)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_results(self, soup):
        any_results = False
        for result in soup.select('div#all'):
            for links in result.select('figure a'):
                link = links['href']
                title = links.text
                if '/actors/' in link:
                    continue
                elif '/seires/' in link:
                    seasons_soup = self.get_soup(link)
                    seasons = seasons_soup.find('p', id='seasonsno').find_all('a')
                    for season in seasons:
                        episode_soup = self.get_soup(season['href'])
                        for episode_links in episode_soup.select('h4.media-heading a'):
                            episode_link = episode_links['href']
                            episode_text = episode_links.text
                            index_page_title = self.util.get_page_title(episode_soup)
                            season, episode = self.util.extract_season_episode(episode_link)
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                series_season=season,
                                series_episode=episode,
                                link_url=episode_link,
                                link_title= episode_text
                            )
                else:
                    self.submit_search_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=link,
                        link_title=title,
                    )
                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def parse(self, page_url, **extra):
        self.webdriver().get(page_url)
        soup = self.make_soup(self.webdriver().page_source)
        title = soup.select_one('h1')
        if title and title.text:
            title = title.text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('td[class="name hover"]'):
            link = base64.decodestring(
                link['data-bind'].split('data,')[1].replace("'", "").replace(")", "").split('/')[-1].split('%')[
                    0] + '==')
            self.submit_parse_result(
                index_page_title=index_page_title,
                series_season=season,
                series_episode=episode,
                link_url=link,
                link_title=title
            )

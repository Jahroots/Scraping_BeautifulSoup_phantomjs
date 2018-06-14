# coding=utf-8

from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase, SimpleScraperBase

class GnulaSe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://gnula.se'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/function.php?id=search',
                data={
                        'key':search_term,
                        'keyword':'title',
                        'genre':'',
                        'search_type':'serie'
                }
            )
        )

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('li.ui-menu-item a'):
            link = self.BASE_URL+result['href']
            ep_soup = self.get_soup(link)
            for ep_link in ep_soup.select('td.episode-title a'):
                title = ep_link.text.strip()
                season, episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=ep_link['href'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode,
                )
                found = 1
        if not found:
            return self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1.underline').text.strip()
        season, episode = self.util.extract_season_episode(title)
        for result in soup.select('table.episodes td.episode-server a'):
            link = result['href']
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link,
                link_title=title,
                series_season=season,
                series_episode=episode,
            )

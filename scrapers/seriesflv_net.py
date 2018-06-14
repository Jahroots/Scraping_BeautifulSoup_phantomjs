# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class SeriesflvNet(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.seriesflv.net'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise  NotImplementedError("The website returns bad gateway error")

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/api/search/?q={}'.format(self.util.quote(search_term))

    def _parse_search_result_page(self, soup):
        on_link = soup.select('a.on')
        if not on_link:
            return self.submit_search_no_results()
        for link in soup.select('a.on'):
            soup = self.get_soup(link['href'])
            page_links = soup.select('div#accordion a.color4')
            for page_link in page_links:
                episode_link = page_link['href']
                self.submit_search_result(
                        link_url=episode_link,
                        link_title=page_link.text.strip(),
                    )

    def _parse_parse_page(self, soup):
            iframes = soup.find('div', id='repro').find_all('iframe')
            for iframe in iframes:
                link = iframe['src']
                title = soup.find('h1').text
                season, episode = self.util.extract_season_episode(title)
                self.submit_parse_result(index_page_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         link_url=link)

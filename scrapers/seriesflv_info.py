# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class SeriesflvNetInfo(SimpleScraperBase):
    BASE_URL = 'http://www.seriesflv.info'
    SINGLE_RESULTS_PAGE = True
    # USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; hu-HU; rv:1.7.8) Gecko/20050511 Firefox/1.0.4'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/series/?q={}'.format(self.util.quote(search_term))

    def _parse_search_results(self, soup):
        found=0
        for link in soup.select('div.title_movie a'):
            soup = self.get_soup(self.BASE_URL+link['href'])
            page_links = soup.select('a.episode')
            for page_link in page_links:
                episode_link = page_link['href']
                season, episode = self.util.extract_season_episode(page_link.text.strip())
                self.submit_search_result(
                        link_url=episode_link,
                        link_title=page_link.text.strip(),
                        series_season=season,
                        series_episode=episode
                    )
                found=1
        if not found:
                return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
            links = soup.find_all('a', text='Reproducir')
            title = soup.find('div', 'title_serie').text
            for link in links:
                link = link.find_next('input')['value']
                season, episode = self.util.extract_season_episode(soup._url)
                self.submit_parse_result(index_page_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         link_url=link)
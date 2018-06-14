# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import requests


class OnlinebioskopCo(SimpleScraperBase):
    BASE_URL = 'https://www.fenixsite.com'
    OTHER_URLS = ['http://www.fenixsite.com', 'http://www.onlinebioskop.co']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'bos'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True


    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(OnlinebioskopCo, self).setup()


    def read(self, url):
        content = requests.get(url, verify= False)
        return content.text

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Request returned no results'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'»')
        if next_button:
            return 'http:'+next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        content = self.read(self._fetch_search_url(search_term, media_type))
        self._parse_search_result_page(self.make_soup(content))

    def _parse_search_result_page(self, soup):
        if not soup.select('div.eTitle a') and len(soup.select('div.eTitle a')) == 0:
            return self.submit_search_no_results()

        for result in soup.select('div.eTitle'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.video-responsive iframe'):
            if 'test.html' in link['src']:
                continue
            if len(link['src']) > 1:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        version_links = self.util.find_urls_in_text(soup.find('div', id='player1').find_next('script').text)
        for version_link in version_links:
            if '...' in version_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=version_link,
                link_title=version_link,
                series_season=series_season,
                series_episode=series_episode,
            )

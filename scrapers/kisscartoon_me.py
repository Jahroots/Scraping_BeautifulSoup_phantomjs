# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class KisscartoonMe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://kisscartoon.ac'
    OTHER_URLS = ['https://kisscartoon.io', 'https://kisscartoon.me', 'https://kisscartoon.es']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/Search/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Not found"

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('a.item_movies_link'):
            image = self.util.find_image_src_or_none(results, 'img')
            result = results['href']
            ep_links = self.get_soup(result).select('div.listing h3 a')
            for ep_link in ep_links:
                self.submit_search_result(
                    link_url=ep_link.href,
                    link_title=ep_link.text,
                    image = image
                )
                found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.replace('Watch Ultimate ', '').replace(' online free', '')
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        if title:
            series_season, series_episode = self.util.extract_season_episode(soup._url)
        ep_id = soup._url.split('?id=')[-1]
        data = {'episode_id':ep_id}
        ep_link = json.loads(
            self.post('{}/ajax/anime/load_episodes'.format(self.BASE_URL),
                      data=data).text)['value']
        if 'http' not in ep_link:
            ep_link = 'https:'+ep_link

        play_list_links = json.loads(self.get(ep_link, headers={'referer':soup._url}).text)['playlist']
        for play_list_link in play_list_links:
            if 'file' in play_list_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=play_list_link['file'],
                    series_season=series_season,
                    series_episode=series_episode
                )
            elif 'sources' in play_list_link:
                for source in play_list_link['sources']:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=source['file'],
                        series_season=series_season,
                        series_episode=series_episode
                    )

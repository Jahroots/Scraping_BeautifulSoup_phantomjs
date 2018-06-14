# coding=utf-8
import re
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class MphimNet(SimpleScraperBase):
    BASE_URL = 'http://www.mphim.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tai'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/danh-sach-phim/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 403,], **kwargs)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[rel="next"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('ul.list_m li.serial h2'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        xem_link = self.get_soup(soup._url).find('a', 'bt_xemphim button').href
        xem_soup = self.get_soup(xem_link)
        link_url = xem_soup.text.split('server":')[-1].split('",')[0].strip('"')
        key = xem_soup.text.split('key":')[-1].split('"}')[0].strip('"')
        if link_url:
            download_link = link_url.replace('\\', '')
            key = key
            link = download_link+key
            links_text = json.loads(self.get(link).text)
            source_links = links_text['data']['sources']
            for source_link in source_links:
                if False == source_link['src']:
                    continue
                link = source_link['src']
                if source_link['src'].startswith('http://api.phimnhanh.com/get_link.php'):
                    link = self.get_redirect_location(link)

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

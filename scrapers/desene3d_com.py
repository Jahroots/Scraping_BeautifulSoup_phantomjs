# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Desene3dCom(SimpleScraperBase):
    BASE_URL = 'http://desene3d.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Rezultate 0-0'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'»')
        if next_button:
            return 'http:'+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.eTitle'):
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
        season = episode = None
        title = soup.select_one('title')
        if title and title.text:
            season, episode = re.findall('Sezonul (\d+)\s', title.text), re.findall('Episodul (\d+)\s',title.text)
            if season:
                season = season[0]
            if episode:
                episode = episode[0]
        for link in soup.select('td.eText iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link['src'],
                series_season=season,
                series_episode=episode,
            )
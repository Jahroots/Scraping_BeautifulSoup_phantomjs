# coding=utf-8
import base64
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class WebrlsCom(CloudFlareDDOSProtectionMixin, OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://top-rel.com'
    OTHER_URLS = ['http://tv-relz.com', 'http://tv-rels.com', 'http://tvrels.com', 'http://tv-rlz.com', 'http://tvrlz.com', 'http://tv-rls.net', 'http://tv-rls.com', 'http://webrls.com', 'http://webrls.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    REQUIRES_WEBDRIVER = True
    LONG_SEARCH_RESULT_KEYWORD = 'delirium'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'uuV5zY6q'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#dle-content h2')[1:]:
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result.find_next('div'), 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        results = soup.select('div.quote a')
        for result in results:
            if 'javascript:void(0)' in result.href:
                continue
            elif 'go.php' in result.href:
                decoded_url = self.util.unquote(result.href.split('url=')[-1])
                link = base64.decodestring(decoded_url)
            else:
                link = result.href
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )
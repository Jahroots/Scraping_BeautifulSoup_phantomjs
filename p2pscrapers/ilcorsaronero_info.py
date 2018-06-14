# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class IlcorsaroneroInfo(SimpleScraperBase):
    BASE_URL = 'http://ilcorsaronero.info'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        time.sleep(1)
        return super(self.__class__, self).get(url, allowed_errors_codes=[104], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/argh.php?search={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('a.tab'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('font[size="+1"]')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        cerca = soup.select_one('form#dlform input[name="cerca"]')['value']
        torrage = '9'
        data = {'cerca':cerca, 'site':torrage}
        itorrents_soup = self.post_soup(soup._url, data=data)
        torrent_link = 'http:'+itorrents_soup.select('frameset frame')[-1]['src']
        self.submit_parse_result(
            index_page_title=index_page_title,
            link_url=torrent_link,
            link_title=torrent_link,
            series_season=series_season,
            series_episode=series_episode,
        )

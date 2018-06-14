# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class MyvideoAz(SimpleScraperBase):
    BASE_URL = 'http://www.myvideo.az'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/c/search?srch_str={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'По Вашему запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'>')
        if link:
           return self.BASE_URL+'/'+link['href']

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('a.mv_video_title'):
            result = self.BASE_URL+'/'+results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        movie_link = re.search("""\'file\':\ \'(.*)\',""", soup.text)
        if movie_link:
            movie_link = movie_link.groups()[0]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                series_season=season,
                series_episode=episode,
                link_text=title,
            )

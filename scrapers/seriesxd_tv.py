# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import base64
import re
class SeriesxdTv(SimpleScraperBase):
    BASE_URL = 'https://repelis.tv'
    OTHER_URLS = ['http://www.seriesxd.tv']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'

    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?s={}'.format(self.util.quote(search_term))

    def setup(self):
        raise NotImplementedError('Deprecated, Duplicate of RepelisTV')

    def _fetch_no_results_text(self):
        return u'0 resultados encontrados'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text = '>>')
        if next:
            return next.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('a[class="info-title one-line"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text

            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('a[href*="iframe"]')
        for result in results:
            text = self.get(result.href).text
            m = re.search(r'Player.decode\(.*\)', text)
            domain = base64.decodestring(m.group(0).split(',')[1].replace("Player.decode('", '').replace("')", ''))
            id = base64.decodestring(m.group(0).split(',')[2].replace("Player.decode('", '').replace("')", ''))

            season, episode = self.util.extract_season_episode(title)
            for result in results:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=domain + '/' + id,
                    link_text=title,
                    series_season=season,
                    series_episode=episode,
                )



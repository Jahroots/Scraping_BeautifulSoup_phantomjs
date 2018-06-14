# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SeriesparaassistironlineOrg(SimpleScraperBase):
    BASE_URL = 'https://seriesparaassistironline.org'
    OTHERS_URLS = ['http://seriesparaassistironline.org']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'não encontrado'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.titulo a'):
            result = results['href']
            title = results.text
            season, episode = self.util.extract_season_episode(title)
            self.submit_search_result(
                link_url=result,
                link_title=title,
                series_season = season,
                series_episode = episode,
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('div.titulo').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        for movie_link in soup.select('div.meio p iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link['src'],
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
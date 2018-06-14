# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class XnZoneTelchargementIwbCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = u'http://www.zone-teléchargement.com'
    OTHER_URLS = ['http://www.xn--zone-telchargement-iwb.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.base'):
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
        results = soup.select_one('div#dle-content div.maincont')
        images = results.find('img', attrs={'src':'http://img3.moviz.net/prez/dl_film.png'})
        if images:
            images = images.find_all_next('a')
            if images:
                for link in images:
                    if self.OTHER_URLS[0] in link.href or self.BASE_URL in link.href:
                        break
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
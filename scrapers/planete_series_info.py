# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class PlaneteSeriesInfo(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://2018.planet-series.co'
    OTHER_URLS = ['http://www.telecharger.planet-series.co',
                  'http://www.planet-series.co',
                  'http://www.planete-series.info',
                  'http://www.telechargement.planete-series.info',
                  ]
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    #LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False

    def setup(self):
        raise NotImplementedError('Duplicate of StreamDownOrg')

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return None#u'La recherche n a retourné aucun résultat'

    def _parse_search_result_page(self, soup):
        results = soup.select('div.full-story div.post-title ')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
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
        for result in soup.find_all('a', text=u"Télécharger"):
            security_soup = self.get_soup(result.href)
            link = security_soup.select_one('div#hideshow a')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

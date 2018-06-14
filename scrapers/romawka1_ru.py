# -*- coding: utf-8 -*-
import base64
import urllib

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Romawka1(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://romawka1.ru'

    def setup(self):
        raise NotImplementedError('Deprecated. Domain is for sale.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    # def search(self, search_term, media_type, **extra):
    #     soup = self.post_soup(self.BASE_URL, data=dict(do='search', subaction='search', story=search_term))
    #     self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.story_h h2 a'):
            found = True
            self.submit_search_result(link_url=link['href'],
                                      link_title=link.text
                                      )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.story_h h2').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.story .text_spoiler a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http://' + link.text if not link.text.startswith('http') else link.text,
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

        for link in soup.select('.story_text a'):
            href = link['href']

            if href.startswith(self.BASE_URL + '/engine/go.php?url='):
                try:
                    href = base64.urlsafe_b64decode(urllib.unquote(href[37:]))
                    if not href.endswith('.jpeg'):
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url='http://' + href if not href.startswith('http') else href,
                                                 link_text=title,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )
                except Exception as e:
                    self.log.exception(e)

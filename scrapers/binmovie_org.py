# -*- coding: utf-8 -*-

import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class BinMovie(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://binmovie.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 0, tv 90'
        # self.encode_search_term_to = 'utf256'
        # self.showposts = 0

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('.shd a'):
            self.submit_search_result(link_url=result['href'],
                                      link_title=result.text)

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.shd').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for dl in soup.select('.quote a'):
            href = dl.href
            if dl['href'].split('/') > 3 and 'ipicture.ru' not in href:

                if href.startswith('http://binmovie.org/engine/go.php?url='):
                    href = base64.decodestring(self.util.unquote(dl.href.split('go.php?url=')[1]))

                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=href,
                                         link_text=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for dl in soup.select('.maincont a'):
            href = dl.href
            if (dl.attrs.get('target', '') == "_blank"
                and 'ipicture.ru' not in href
                and 'picplus.ru' not in href
                and 'binimage.org' not in href):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=href,
                                         link_text=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

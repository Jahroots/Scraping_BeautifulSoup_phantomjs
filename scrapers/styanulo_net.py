# -*- coding: utf-8 -*-
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class StyanuloNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://styanulo.net'
    TRELLO_ID = 'DH2cmP8P'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _parse_search_results(self, soup):
        any_results = False
        for result in soup.select('div.cbox'):
            link = result.select('h3.btl a')
            if not link:
                continue

            self.submit_search_result(
                link_url=link[0]['href'],
                link_title=link[0].text,
                image=self.util.find_image_src_or_none(result, 'div.maincont img')
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        ttl = soup.select_one('.titlel > h1').text

        for link in soup.select('a[href*="/out"]'):
                # paydirt.
                link_url = self.get_redirect_location(
                    self.BASE_URL + link['href'])

                if link_url:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link_url,
                                             link_title=ttl
                                             )

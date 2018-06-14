# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable



class GamatotvMe(SimpleScraperBase):

    BASE_URL = 'http://gamatotv.me'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'gre'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Δεν βρέθηκαν αποτελέσματα για το'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/groups/group/search?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Επόμενο ›')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3 a'):
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.xg_user_generated a'):
            if link.href.startswith('http'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['href'],
                    link_title=link.text,
                    )


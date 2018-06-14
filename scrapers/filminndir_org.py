# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmInndirOrg(SimpleScraperBase):
    BASE_URL = 'http://filminndir.net'

    def setup(self):
        raise NotImplementedError('Deprecated. Website no longer available')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'tur'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}&x=0&y=0'.format(search_term)

    def _fetch_no_results_text(self):
        return 'XXX'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Son Sayfa»')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('h5.title a'):
            found = True
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # http://filminndir.org/out/http://turbobit.net/3ax11pfjz2m8/Yenilmezler.Ultron.Cagi.2015.TR.BRRip.XviD.avi.html
        #Links only
        for link in soup.select('a[href*="' +self.BASE_URL +'/out/"]'):

            if 'imdb' not in link.href:
                self.submit_parse_result (
                    index_page_title = self.util.get_page_title(soup),
                    link_url=link['href'].split('/out/')[1],
                )

        #Video online
        iframes = soup.select('iframe[allowfullscreen]')
        for iframe in iframes:
            src = iframe['src']
            if src and 'youtube' not in src:
                if src.find('http:') == -1:
                    src = 'http:' + src

                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=src
                )
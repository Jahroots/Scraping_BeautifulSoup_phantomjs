# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmesMegaHD(SimpleScraperBase):
    BASE_URL = 'http://www.filmesmegahd.net'

    def setup(self):
        raise NotImplementedError('Deprecated. Website has no parse results.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'por'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class*="box-video"] a')

        if not results or len(results) ==0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.titulo-destaque').text.strip()

        for link in soup.select('div.embeds-servidores div.embeds-video iframe'):
            href = link['data-lazy-src']

            if href.find('http') == -1:
                href = 'https:' + href

            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=href,
                link_title=title
            )

    def get(self, url, **kwargs):
        kwargs['headers'] = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0',}
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)
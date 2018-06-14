# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FusionDescargasNet(SimpleScraperBase):
    BASE_URL = 'http://www.fusiondescargas.net'

    def setup(self):
        raise NotImplementedError('The website is deprecated')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No se encontraron resultados'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.tp2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.tp').text.strip()
        season, episode = self.util.extract_season_episode(title)
        #get redirect link
        hidden_link = soup.select_one('p a[href*="ocultador.com"]')
        soup1 = self.get_soup(hidden_link['href'])
        #call the hidden link to get the url
        bypass = self.get_soup('http://ocultador.com/' + soup1.select_one('iframe')['src'])
        self.log.debug(soup1.select_one('iframe')['src'])
        
        link = bypass.select_one('#thepaste')

        if link and link.text and len(link.text.split('http')) > 1 :
            link = link.text.split('http')[1].strip()

            if link.find('http') == -1:
                link = 'http' + link

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link,
                link_title=title,
                series_season=season,
                series_episode=episode
            )

    def get(self, url, **kwargs):
        return super(FusionDescargasNet, self).get(url, allowed_errors_codes=[404], **kwargs)

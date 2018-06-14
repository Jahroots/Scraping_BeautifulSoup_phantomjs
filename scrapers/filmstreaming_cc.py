# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import CloudFlareDDOSProtectionMixin


class FilmStreaming(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://filmstreaming.cc'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        raise NotImplementedError('Domain Not Available.')



    def _fetch_no_results_text(self):
        return u'Désolé, aucun film trouvé.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.movief a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.title.text.split('|')[0].strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.findAll('script'):
            if 'src' in link and link['src'].startswith('http://hqq.tv/player/hash.php'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['src'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

        for fr in soup.findAll('iframe', allowfullscreen="true"):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=fr['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

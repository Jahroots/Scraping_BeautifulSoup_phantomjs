# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DVDRipFilms(SimpleScraperBase):
    BASE_URL = 'http://www.dvdripfilms.com'
    OTHER_URLS = ['http://dvdripfilms.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self._request_size_limit = (1024 * 1024 * 5)  # Bytes
        raise NotImplementedError

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'Aucun résultat trouvé'

    def _parse_search_result_page(self, soup):
        for link in soup.select('.image-post-title a'):
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='›')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.entry-title.single-post-title').text
        season, episode = self.util.extract_season_episode(title)

        # CAPTCHA protected

        for link in soup.select('#result p a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

        for link in soup.select('.link'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.parent.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

        for link in soup.select('.post_content p a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

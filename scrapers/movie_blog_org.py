# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MovieBlog(SimpleScraperBase):
    BASE_URL = 'http://movie-blog.org'
    OTHER_URLS = ['http://www.movie-blog.org']

    LONG_SEARCH_RESULT_KEYWORD = 'the night'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ger'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?s={}&cat=0'.format(search_term)

    def _fetch_no_results_text(self):
        return u'Diese Filme stehen nur registrierten Benutzern zur Verfügung'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.nextpostslink')
        self.log.debug('-' * 30)
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.post h1 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.fn').text

        season, episode = self.util.extract_season_episode(title)

        for vid in soup.select('.eintrag2 p a')+soup.select('.sp-body p a'):
            try:
                if vid.startswith_http:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=vid.href,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
            except Exception as e:
                self.log.exception(e)
                # self.show_in_browser(soup)
                raise e

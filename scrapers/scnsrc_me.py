# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class ScnsrcMe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.scnsrc.me'

    OTHER_URLS = ['http://scnsrc.me', 'http://www.scnsrc.me', ]
    SEARCH_TERM = ''

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in self.OTHER_URLS + [self.BASE_URL, ]:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '?s={}&x=0&y=0'.format(self.SEARCH_TERM)

    def _fetch_no_results_text(self):
        return 'Sorry, no posts matched your criteria'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a.nextpostslink')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        super(ScnsrcMe, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        for result in soup.select('.post h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post h2').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('#comment_list a'):
            movie_link = None
            try:
                movie_link = link['href']
            except KeyError:
                pass
            if movie_link:
                if link['href'].startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link['href'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

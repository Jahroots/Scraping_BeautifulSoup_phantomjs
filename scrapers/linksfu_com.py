# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class LinksFu(SimpleScraperBase):
    BASE_URL = 'http://wantdl.com'
    OTHER_URLS = ['http://linksfu.com']

    def setup(self):
        raise NotImplementedError('Deprecated. Website no longer available.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'did not match any entries.'

    def _parse_search_result_page(self, soup):
        for link in soup.select('.stitle a'):
            self.submit_search_result(
                ink_title=link.text,
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.title h2').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.ext-link'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(), link_title=title,
                                     link_url=link.text,
                                     series_season=series_season,
                                     series_episode=series_episode
                                     )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TopMovies21(SimpleScraperBase):
    BASE_URL = 'http://filmbaru.icinema3satu.xyz'
    OTHER_URLS = ['http://topmovies21.heck.in']
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?search=' + search_term

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.title a'):
            found = True
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )
        if not found:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'No results found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.entry ul li a'):
            if not link.href.startswith(self.BASE_URL) and link.href.startswith('http'):

                try:
                    url = 'http://adf.ly/?id=' + self.get(link.href).text.split('http://adf.ly/?id=')[1].split('"')[0]

                    self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
                except Exception as e:
                    # print link.href
                    # self.log.exception(e)
                    # print(self.get(link.href).text)
                    # raise

                    # Sometimes redirects to CloudFlare ...
                    pass

        dload_btn = soup.find('img', title="Download Here")
        if dload_btn:
            self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=dload_btn.parent.href,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

        morelinks = soup.find('a', text='HostLinks')
        if morelinks:
            soup_more = self.get_soup(morelinks.href)
            for lnk in soup_more.find_all('a', rel="nofollow"):
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=lnk.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

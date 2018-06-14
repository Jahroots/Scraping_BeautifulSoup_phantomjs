# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Projectfreetv_Us(SimpleScraperBase):
    BASE_URL = 'http://projectfreetv.us'

    # Note this site may return results for projectwatchseries.com
    # These are handled in that scraper
    OTHER_URLS = [] #'http://projectwatchseries.com',]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Domain in sale.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL,] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            self.BASE_URL + '/search.php',
            data={'searchText':'{}'.format(search_term), 'md':'all','submit':'Search'
                  }
        )
        search_link = soup.select_one('td.mnlcategorylist a')
        if not search_link:
            return self.submit_search_no_results()
        self._parse_search_results(
            self.get_soup(self.BASE_URL + '/' +search_link['href']))

    def _fetch_no_results_text(self):
        return u'Favourite Shows'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):

        for result in soup.select('td.mnllinklist a.down'):
            self.submit_search_result(
                                link_url=result['href'],
                                link_title=result.text,
                            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div#vvdiv iframe'):
            source_link = link['src']
            title = self.util.get_page_title(soup)
            season, episode = self.util.extract_season_episode(title)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=source_link,
                                     series_season=season,
                                     series_episode=episode,
                                     )


    #     found = False
    #     submitted = set()
    #     for result in soup.select('div#content table tr td.trow1 a'):
    #         if result['href'].startswith('showthread.php'):
    #             url = self.BASE_URL + '/forum/' + result['href']
    #             if url not in submitted:
    #                 self.submit_search_result(
    #                     link_url=url,
    #                     link_title=result.text,
    #                 )
    #                 found = True
    #                 submitted.add(url)
    #     if not found:
    #         self.submit_search_no_results()



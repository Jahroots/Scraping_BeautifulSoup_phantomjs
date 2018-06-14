# coding=utf-8

import re

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class MamzoukaComFilm(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.mamzouka.com'
    OTHER_URLS = ['http://mamzouka.com', 'http://mamzouka.com', ]
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)


    def _fetch_no_results_text(self):
        return u"La recherche n a retourné aucun résultat."

    def _parse_search_result_page(self, soup):
        for result in soup.select('#dle-content div.shortf-img'):
            link = result.select_one('a')

            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.util.find_image_src_or_none(link, 'img'),
                asset_type=ScraperBase.MEDIA_TYPE_FILM
            )

    def _parse_parse_page(self, soup):
        # Simple iframes.
        for iframe in soup.select('div.video-responsive iframe'):
            if iframe['src'].startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=iframe['src'],
                                         asset_type=ScraperBase.MEDIA_TYPE_FILM
                                         )


# class MamzoukaComTv(MamzoukaComFilm, SimpleScraperBase):
#     BASE_URL = 'http://mamzouka.com'
#     OTHER_URLS = ['http://series.mamzouka.com', ]

    # def setup(self):
    #     self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
    #     self.search_term_language = "fra"
    #
    #     self.register_media(ScraperBase.MEDIA_TYPE_TV)
    #
    #     self.register_url(
    #         ScraperBase.URL_TYPE_SEARCH,
    #         self.BASE_URL)
    #
    #     self.register_url(  # FIXME    not sure
    #         ScraperBase.URL_TYPE_LISTING,
    #         self.BASE_URL)
    #
    # def _fetch_no_results_text(self):
    #     return 'No posts yet'
    #
    # def _fetch_next_button(self, soup):
    #     link = soup.find('a', text='›')
    #     if link:
    #         return link['href']
    #     return None
    #
    # def _extract_season(self, text):
    #     season_match = re.search('[s|S]aison (\d+)', text)
    #     if season_match:
    #         return season_match.group(1)
    #     return None
    #
    # def _parse_search_result_page(self, soup):
    #     for result in soup.select('div.posts li.clearfix'):
    #         image = result.select('div.imageholder a img')[0]
    #         link = result.select('h2.custom-font a')[0]
    #         series_season = self._extract_season(link.text)
    #         self.submit_search_result(
    #             link_url=link['href'],
    #             link_title=link.text,
    #             image=image['src'],
    #             series_season=series_season,
    #             asset_type=ScraperBase.MEDIA_TYPE_TV
    #         )
    #
    # def _parse_parse_page(self, soup):
    #     page_title = soup.find('h1', 'heading').text
    #     series_season = self._extract_season(page_title)
    #     for episode in soup.select(
    #             'div.shortcodes-tabs > div'):
    #         # The id of the tab appears to correlate to episodes.
    #         series_episode = self.util.find_numeric(episode['id'])
    #         if series_episode is not None:
    #             series_episode += 1
    #         for iframe in episode.select('iframe'):
    #             url = iframe['src']
    #             self.submit_parse_result(index_page_title=soup.title.text.strip(),
    #                                      link_url='http:' + url if url.startswith('//') else url,
    #                                      link_title=page_title,
    #                                      series_season=series_season,
    #                                      series_episode=series_episode,
    #                                      asset_type=ScraperBase.MEDIA_TYPE_TV
    #                                      )

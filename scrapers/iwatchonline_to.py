# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin

class IWatchOnlineTo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.watchonline.to'
    OTHER_URLS = ['https://www.iwatchonline.to', 'https://www.iwatchonline.cr']


    LONG_SEARCH_RESULT_KEYWORD = 'rock 2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

        for url in (
                self.BASE_URL,
                'http://www.iwatchonline.to',
                'https://www.imovie.to',
                'https://www.iwatchonline.ag',
                'http://www.iwatchonline.ph'
        ):
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)



    def search(self, search_term, media_type, **extra):
        parse_func = None
        searchin = None
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            searchin, parse_func = ('t', self._parse_search_tv)
        elif media_type == ScraperBase.MEDIA_TYPE_FILM:
            searchin, parse_func = ('m', self._parse_search_film)

        soup = self.post_soup(
            self.BASE_URL + '/search',
            data={
                'searchin': searchin,
                'searchquery': self.util.quote(search_term)
            }
        )

        parse_func(soup)


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        links = soup.select('a[class="spf-link Blockit"]')
        for link in links:
            link = self.get(link.href).headers['Refresh'].split('url=')[-1]

            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=link,
                                     )

    def _parse_search_tv(self, soup):
        found = 0
        for link in soup.select('div[class="widget search-page"] table[class="table table-striped table-hover"] td a[href*="' + self.BASE_URL +'"]'):
            self.submit_search_result(
                    link_url=link['href'],
                    link_title=link.text.strip(),
                    asset_type=ScraperBase.MEDIA_TYPE_FILM
                )
            found=1
        if not found:
            return self.submit_search_no_results()

        # links = list(
        #     self.get_soup_for_links(soup, 'div[class="widget search-page"] td a')
        # )
        # if not links:
        #     return self.submit_search_no_results()
        #
        #
        #
        # for link, season_soup in links:
        #     if not link or not link['href'].startswith('http'):
        #         continue
        #     for season_block in season_soup.select('div.accordion-group'):
        #         heading = season_block.select('div.accordion-heading h5')[0]
        #         season = self.util.find_numeric(heading.text)
        #         for episode_link, episode_soup in \
        #                 self.get_soup_for_links(season_soup,
        #                                         'div.accordion-body table a'):
        #             episode = self.util.find_numeric(episode_link.text)
        #
        #             # This is functionally the sam as the movie page.
        #             for video_link in episode_soup.select('div.movie-links td.sideleft a[class="spf-link KAKA"]'):
        #                     self.submit_search_result(
        #                         link_url=video_link['href'],
        #                         link_title=video_link.text.strip(),
        #                         asset_type=ScraperBase.MEDIA_TYPE_TV,
        #                         series_season=season,
        #                         series_episode=episode,
        #                     )



    def _parse_search_film(self, soup):
        # links = list(
        #     self.get_soup_for_links(soup, 'div[class="widget search-page"] td a')
        # )
        # if not links:
        #     return self.submit_search_no_results()
        #
        #
        #
        # for link, page_soup in links:
        #     if not link or not link['href'].startswith('http'):
        #         continue
        #
        #     for video_link in page_soup.select('div.movie-links td.sideleft a'):
        #         if video_link['href'].startswith('http'):
        #             self.submit_search_result(
        #                 link_url=video_link['href'],
        #                 link_title=video_link.text.strip(),
        #                 asset_type=ScraperBase.MEDIA_TYPE_FILM
        #             )
        found=0
        for link in soup.select('div[class="widget search-page"] table[class="table table-striped table-hover"] td a[href*="' + self.BASE_URL +'"]'):
            self.submit_search_result(
                    link_url=link['href'],
                    link_title=link.text.strip(),
                    asset_type=ScraperBase.MEDIA_TYPE_FILM
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

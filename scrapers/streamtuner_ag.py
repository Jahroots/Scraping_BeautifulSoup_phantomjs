# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class StreamtunerAg(SimpleScraperBase):
    BASE_URL = 'http://streamtuner.xyz'
    OTHER_URLS = ['http://streamtuner.li','http://streamtuner.ag', 'http://streamtuner.pw', 'http://series-cravings.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/{search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Sorry, but there is no tv series available for the keyword'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.nav-previous a')
        if next_button:
            return next_button.href
        return None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404,403, ], **kwargs)

    def _parse_search_result_page(self, soup):
        for result in soup.select('article h1.entry-title'):
            link = result.select_one('a').href
            for dowload_link in self.get_soup(link).select('div.entry-content ul li a'):
                if '-in-hd' in dowload_link.href:
                    continue
                if dowload_link.href:
                    self.submit_search_result(
                        link_url=dowload_link.href,
                        link_title=dowload_link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
            for season_image_link in self.get_soup(link).select('div.entry-content img.alignnone'):
                season_link = season_image_link.find_previous('a').href
                for dowload_link in self.get_soup(season_link).select('div.entry-content ul li a'):
                    if '-in-hd' in dowload_link.href:
                        continue
                    if dowload_link.href:
                        self.submit_search_result(
                            link_url=dowload_link.href,
                            link_title=dowload_link.text,
                            image=self.util.find_image_src_or_none(result, 'img'),
                        )


    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('b[data-iframe]'):
            link = self.make_soup(link['data-iframe']).select_one('iframe')
            if link and link.has_attr('src'):

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

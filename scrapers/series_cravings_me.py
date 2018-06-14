# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SeriesCravingsMe(SimpleScraperBase):
    BASE_URL = 'http://seriescravings.li'
    OTHER_URLS = ['http://series-cravings.tv', 'http://series-cravings.li',
                  'http://series-cravings.me', ]
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{}/?s={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search criteria.'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.nav-previous a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):

        results = soup.select('article h1.entry-title a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('article h1.entry-title'):
            link = result.select_one('a')
            image = self.util.find_image_src_or_none(result, 'img')

            series_soup = self.get_soup(link.href)
            for episode in series_soup.select('div.entry-content div.omsc-toggle ul.b li a'):
                self.submit_search_result(
                    link_url=episode.href,
                    link_title=episode.text,
                    image=image,
                )

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1.entry-title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('b'):
            iframe = link.get('data-iframe', None)
            if iframe:
                iframe_soup = self.make_soup(iframe)
                for iframe in iframe_soup.select('iframe'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=iframe['src'],
                        series_season=series_season,
                        series_episode=series_episode,
                    )

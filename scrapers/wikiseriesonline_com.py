# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class WikiseriesonlineCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.wikiseriesonline.nu'
    OTHER_URLS = ['http://www.wikiseriesonline.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[504, 522,], **kwargs)

    def setup(self):
        super(WikiseriesonlineCom, self).setup()
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True
        self._request_connect_timeout = 600
        self._request_response_timeout = 600

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'No hay entradas'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):

        for result in soup.select('div.search-results-information'):
            link = result.select_one('a')
            soup = self.get_soup(link.href)
            results = soup.select('div.box-player')

            for item in results:
                link = item.select_one('a')
                self.submit_search_result(
                    link_url=self.BASE_URL + link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(item, 'img'),
                )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('div[class="row box-repro-title"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('div[class*="embed-responsive"] iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                season = season,
                episode = episode
            )

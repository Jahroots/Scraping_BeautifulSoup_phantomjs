# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class ScnlogEu(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://scnlog.me'
    OTHER_URLS = ['https://scnlog.eu']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False

    def _fetch_no_results_text(self):
        return u"Sorry, but you are looking for something that isn't here."

    def _fetch_next_button(self, soup):
        link = soup.find('strong', text='»')
        self.log.debug('------------------------')
        return link.parent['href'] if link else None

    def search(self, search_term, media_type, **extra):
        self._search_term = search_term
        self._media_type = media_type
        return super(ScnlogEu, self).search(search_term, media_type, **extra)

    def _fetch_search_url(self, search_term, media_type):
        return '{}?s={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _get_cloudflare_action_url(self):
        return self._fetch_search_url(self._search_term, self._media_type)
    
    def _parse_search_result_page(self, soup):
        for result in soup.select('div.title h1'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image= self.BASE_URL + self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.download a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

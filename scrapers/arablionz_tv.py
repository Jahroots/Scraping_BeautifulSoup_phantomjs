# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin

class ArablionzTv(SimpleScraperBase):
    BASE_URL = 'http://arablionz.online'
    OTHER_URLS = ['http://arab-lionz.com', 'http://arablionz.tv', 'http://arablionz.com', 'http://arablionz.tv', 'http://forums.arablionz.tv', 'http://arablionz.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    PAGE = 0

    def setup(self):
        self.PAGE = 0
        super(self.__class__, self).setup()
        self._request_connect_timeout = 400
        self._request_response_timeout = 400

    def _fetch_no_results_text(self):
        return None


    def _fetch_next_button(self, soup):
        a = soup.find('a', text=u'الصفحة التالية «')
        link = None
        if a:
            link = a['href']

        return link if link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.select('div[class*="BlocksMovList loadPosts"] a.BlockMov')
        if not blocks:
            return self.submit_search_no_results()
        for block in blocks:
            page_link = block['href']
            title = self.util.get_page_title(soup)

            self.submit_search_result(
                    link_url=page_link,
                    link_title=title,
            )


    def _parse_parse_page(self, soup):
        links = soup.select('a')
        index_page_title = self.util.get_page_title(soup)
        #self.log.warning(index_page_title)
        #self.log.warning(soup)
        #season, episode = self.util.extract_season_episode(index_page_title)

        iframes = soup.select('div.tvScreen iframe[data-src]')
        for iframe in iframes:
            self.submit_parse_result(index_page_title=index_page_title,
                                     #series_season=season,
                                     #series_episode=episode,
                                     link_url=iframe['data-src'])

        url = soup.select('div.buttonsB a')[-1]
        if url and 'forum' in url.href:
            aux= self.get_soup(url.href)
            links = aux.select('a[href*="http://uplds.com"]')
            for link in links:
                a = self.get_soup(link.href)
                a = a.select_one('input[name="id"]')['value']
                self.submit_parse_result(index_page_title=index_page_title,
                                         series_season=season,
                                         series_episode=episode,
                                         link_url= a)
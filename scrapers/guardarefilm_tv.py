# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class GuardarefilmTv(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.guardarefilm.life'
    OTHER_URLS = ['https://www.guardarefilm.live', 'http://www.guardarefilm.live', 'https://www.guardarefilm.zone', 'http://www.guardarefilm.gratis','http://www.guardarefilm.biz', 'https://www.guardarefilm.uno', 'http://www.guardarefilm.tv', 'http://www.guardarefilm.me', 'http://www.guardarefilm.eu']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    WEBDRIVER_TYPE = 'phantomjs'
    REQUIRES_WEBDRIVER = True

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/index.php?do=search_advanced&q={}&section=0&director=&actor=&year_from=&year_to=&cstart={}'.format(search_term, start)

    def _fetch_no_results_text(self):
        return None#u'Nessun risultato trovato, usare la ricerca avanzata oppure cercare nella trama'

    def _parse_search_results(self, soup):
        #no_results_text = self._fetch_no_results_text()
        #if no_results_text and unicode(soup).find(no_results_text) >= 0:
        #    return self.submit_search_no_results()
        results = soup.select('div#dle-content div.label a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )
    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], verify=False, **kwargs)

    def _parse_search_result_page(self, soup):
        rslts = soup.select('div#dle-content div.label a')
        for result in rslts:
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('ul.overview > li > a') + soup.select('div.tab-content ul.reset a.links-sd')
        for result in results:
            series_title= ''
            try:
                series_title = result.find_previous('li')['data-title']
            except KeyError:
                pass
            season, episode = self.util.extract_season_episode(series_title)
            data_link = ''
            try:
                data_link = result['data-link']
            except KeyError:
                pass
            if 'play4k' in data_link or not data_link:
                continue
            if 'http' not in data_link:
                data_link = 'http:'+data_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=data_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )

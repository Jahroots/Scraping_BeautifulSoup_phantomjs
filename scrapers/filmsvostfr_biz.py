# coding=utf-8


from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase


class FilmsvostfrBiz(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'http://filmsvostfr.ws'
    OTHER_URLS = ['http://filmsvostfr.xyz', 'http://www.filmsvostfr.cc', 'http://www.filmsvostfr.co', 'http://www.filmsvostfr.cd']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    SINGLE_RESULTS_PAGE = True
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.get_soup(
                self.BASE_URL + '/recherche.htm?q={}'.format(self.util.quote(search_term))
            )
        )

    def _parse_search_results(self, soup):
        self.block = False
        results = soup.select('div.films-container h4 a')

        for result in results:
            link = result['href']
            ep_soup = self.get_soup(link)
            ep_links = ep_soup.select('div.description ul li a')

            for ep_link in ep_links:
                title = ep_soup.select_one('div.titles_holder').text
                season, episode = self.util.extract_season_episode(ep_link['title'])
                self.submit_search_result(
                    link_url=self.BASE_URL+ep_link['href'],
                    link_title=title+' '+ep_link['title'].strip(),
                    series_season=season,
                    series_episode=episode,
                )
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )
            self.block = True
        if not self.block:
            return self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            title = soup.select_one('h1').text.strip()
            links = soup.select('div.filmelink a[target="filmPlayer"]')
            season, episode = self.util.extract_season_episode(title)
            for l in links:
                self.log.debug(l.href)

                try:
                    soup = self.get_soup(l.href)

                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=soup._url,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode,
                                             )
                except Exception as ex:
                    self.log.error(ex)

            iframe = soup.select_one('iframe')
            if iframe and iframe['src']:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=iframe['src'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )
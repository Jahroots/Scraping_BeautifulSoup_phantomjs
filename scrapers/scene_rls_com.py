# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class SceneRlsCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://scene-rls.net'
    OTHER_URLS = ['http://scene-rls.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        super(self.__class__, self).setup()
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but you are looking for something'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('h2.postTitle a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.postTitle').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        results = soup.find('div', 'postContent').find_all('h2')
        for result in results:
            movie_links = result.find_all('a')
            for movie_link in movie_links:
                if 'nfo.scene-rls' in movie_link['href']:
                    redirect_soup = self.get_soup(movie_link['href'])
                    for redirect_links in redirect_soup.select('div.container a'):
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=redirect_links['href'],
                            link_text=title,
                            series_season=season,
                            series_episode=episode,
                        )
                else:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link['href'],
                        link_text=title,
                        series_season=season,
                        series_episode=episode,
                    )

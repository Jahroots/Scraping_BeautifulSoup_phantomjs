# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SceperUnlockprojectCom(SimpleScraperBase):
    BASE_URL = 'https://sceper.unlockproject.fun'
    OTHER_URLS = ['https://sceper.unlockproj.club', 'https://sceper.unlockpro.club', 'https://sceper.unlockpro.bid', 'https://sceper.unlockproject.info', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None #u'No Results Found'

    def _fetch_next_button(self, soup):
        next_link=''
        try:
            next_link = soup.find('a', text=u'»')
        except AttributeError:
            pass
        if next_link:
            return next_link['href']

    def _parse_search_result_page(self, soup):
        results = soup.select('h2.title a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for results in results:
            title = results.text
            season, episode = self.util.extract_season_episode(title)
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
                series_season=season,
                series_episode=episode,
            )


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.title')
        season = episode = None
        if title:
            title = title.text
            season, episode = self.util.extract_season_episode(title)

        index_page_title = self.util.get_page_title(soup)

        for links in soup.select('p span span a'):
            link = links.text
            if 'http' in link:
               self.submit_parse_result(
                   index_page_title=index_page_title,
                   link_url=link,
                   series_season=season,
                   series_episode=episode,
                   link_text=title,
               )
        for link in soup.find('div', text=u'Download Links').find_next('p').find_all('a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                series_season=season,
                series_episode=episode,
                link_text=title,
            )
# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WatchTvseriesNet(SimpleScraperBase):
    BASE_URL = 'http://1.watch-tvseries.net'
    OTHER_URLS = ['http://www.watch-tvseries.me']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404,], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No result TV Series'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for results in soup.select('div#resultv a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            season, episode = self.util.extract_season_episode(title)
            self.submit_search_result(
                link_url=result,
                link_title=title,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        if '404' in unicode(soup):
            return
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        scripts_text = soup.find('div', id='shareico').find_all_next('script')[2].text.split("morurlvid('")[1:]
        for script_text in scripts_text:
            link_id = script_text.split("',this)")[0]
            if 'morevideo2' in link_id:
                continue
            iframe_soup = self.get_soup('http://www.watch-tvseries.me/play/mvideo_{}'.format(link_id))
            link = iframe_soup.find('div', 'lplayer').find('a')['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )

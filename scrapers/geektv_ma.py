# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json

class GeektvMa(SimpleScraperBase):
    BASE_URL = 'https://shows.geektv.so'
    OTHERS_URLS = ['https://i.geektv.so', 'http://geektv.so' ,'https://geektvonline.ch','http://geektvonline.ch', 'http://geektv.ma']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'is not found in our Database'

    def _fetch_next_button(self, soup):
        return None

    def get(self, url, **kwargs):
        return super(GeektvMa, self).get(url, allowed_errors_codes=[403, ], **kwargs)


    def _parse_search_result_page(self, soup):

        results = soup.select('div.card-block table tr[class*="item"] a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            title = result.text
            url = result.href
            soup = self.get_soup(url)


            episodes = soup.select('a[href*="episode"]')
            for episode in episodes:
                self.submit_search_result(
                            link_url=episode.href,
                            link_title=title
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)

        src = soup.select_one('#player iframe')['src']
        src = self.get_redirect_location(src)

        if src:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_text=title,
                series_season=season,
                series_episode=episode
            )

        for link in soup.select('button[data-id]'):
            link = self.get_redirect_location(self.BASE_URL + '/link/' + link['data-id'])
            if link:
                self.submit_parse_result(
                         index_page_title=index_page_title,
                         link_url=link,
                         link_text=title,
                         series_season=season,
                         series_episode=episode
                     )
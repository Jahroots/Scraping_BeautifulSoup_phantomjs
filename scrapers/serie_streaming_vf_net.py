# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SerieStreamingVfNet(SimpleScraperBase):
    BASE_URL = 'http://series-streaming-vf.com'
    OTHER_URLS = ['http://serie-streaming-vf.cc', 'http://serie-streaming-vf.co', 'http://serie-streaming-vf.tv', 'http://serie-streaming-vf.net', 'http://serie-streaming-vf.org',
                  'http://serie-streaming-vf.biz', 'http://serie-streaming-vf.me']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = '8lHvhGqr'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"utiliser la iste déroulante des Séries pour séléctionner votre série préférée"

    def get(self, url, **kwargs):
        return super(SerieStreamingVfNet, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.postcont div.boxentry a'):
            result = results['href']
            ep_soup = self.get_soup(result)
            ep_links = ep_soup.select('div.keremiya_part a')
            title = ep_soup.select_one('h2').text.strip()
            season, episode = self.util.extract_season_episode(title)
            for ep_link in ep_links:
                title = results.text
                self.submit_search_result(
                    link_url=ep_link['href'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode,
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        results = soup.select('#links a')
        for result in results:
            movie_link = result['href']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
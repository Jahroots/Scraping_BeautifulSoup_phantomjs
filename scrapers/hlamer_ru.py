# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re

# NOte these two sites exchange links within search results.
# so they both have each other as 'OTHER_URLS' for the purpose of fulltest

class HlamerRu(SimpleScraperBase):
    BASE_URL = 'http://kadu.ru'
    OTHER_URLS = ['http://hlamer.ru', 'http://smotri.pro']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def http_session(self):
        self._http_session = None
        super(self.__class__, self).http_session()
        return self._http_session

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/video/search/?query={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = ''
        try:
            next_link = soup.find('div', 'pager').find('a', text=u'→')
        except AttributeError:
            pass
        if next_link:
            return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.video-gallery li div a')
        if not results:
            return self.submit_search_no_results()
        for results in results:
            title = results.find('div', 'text').text
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        srch = re.search("video_Init\(.*? 'url': '(http.*?)\\',", unicode(soup))
        if not srch:
            search_soup = self.get(soup._url).text
            srch = re.search("""['"]*url['"]*\s*:\s*['"](.*?)['"]""", search_soup)
        if srch:
            url = srch.group(1).replace('\\', '')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                series_season=season,
                series_episode=episode,
                link_title=title,
            )
        else:
            self.log.error('Could not find video in %s', soup._url)


class KaduRu(HlamerRu):
    BASE_URL = 'http://kadu.ru'
    OTHER_URLS = ['http://hlamer.ru']

    def setup(self):
        raise NotImplementedError('Deprecated, Duplicated of HlamerRu.')

    def http_session(self):
        self._http_session = None
        return super(HlamerRu, self).http_session()

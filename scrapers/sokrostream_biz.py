# coding=utf-8
import re
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin


class SokrostreamBiz(CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'https://sokrostream.cx'
    OTHER_URLS = ['http://sokrostream.tv', 'http://sokrostream.ws', 'http://sokrostream.cc', 'http://sokrostream.biz', 'http://sokrostream.ws']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fre'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SEARCH_TERM = ''


    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(search_term)

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('a.pagination-next')
        return self.BASE_URL + next_link['href'] if next_link else None

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        try:
            soup = self.get_soup(self._fetch_search_url(search_term, media_type))
            self._parse_search_result_page(soup)
        except Exception as e:
            self.log.warning(str(e))
            if 'Fetch error' in str(e):
                return self.submit_search_no_results()



    def _parse_search_result_page(self, soup):
        blocks = soup.select('a[href*="/films/"]')
        any_results = False
        for block in blocks:
            link = block['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )
            any_results = True

        blocks = soup.select('a[href*="/series/"]')
        for block in blocks:
            link = block['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )
            any_results = True

        if not any_results:
            return self.submit_search_no_results()

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        title = soup.find('h1').text
        data = json.loads(soup.find('script', text=re.compile('"layout":')).text.replace('window.__NUXT__=', '').replace(';', '').strip())

        for item in data['data']:
            videos = item['data']['videos']
            for video in videos:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                    link_url=video['link'],
                    link_title=title
                )

        iframes = soup.select('div.embed-container iframe')
        for iframe in iframes:
            self.submit_parse_result(
                index_page_title=index_page_title,
                series_season=season,
                series_episode=episode,
                link_url=iframe['src'],
                link_title=title
            )



        if '/series/' in soup._url:
            for series in soup.select('a.listefile'):
                series_soup = self.get_soup(series['href'])
                index_page_title = self.util.get_page_title(soup)
                title = series_soup.find('h1').text
                season, episode = self.util.extract_season_episode(index_page_title)
                levideo_ids = series_soup.find_all('li', 'seme')
                for levideo_id in levideo_ids:
                    levideo = levideo_id.find('input', attrs={'name':'levideo'})['value']
                    data = {'levideo':levideo}
                    movie_soup = self.make_soup(self.post(series['href']+'#playfilm', data=data).text)
                    movie_link = movie_soup.find('div', 'bgvv').find('iframe')['src']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        series_season=season,
                        series_episode=episode,
                        link_url=movie_link,
                        link_title=title
                    )
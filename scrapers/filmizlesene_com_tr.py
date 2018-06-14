# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class FilmizleseneComTr(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.fhdfilmizlesene.com'
    OTHER_URLS = ['http://www.filmizlesene.com.tr']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_AGENT_MOBILE = False
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    TRELLO_ID = 'EAptWIBg'


    def _get_cloudflare_action_url(self):
        return self.BASE_URL + '/index.php?s=man'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Uygun Film Bulunamadı'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text =u'İleri ›')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        self.log.debug(soup)
        for results in soup.select('#content div.mkutu2'):
            if not results:
               return self.submit_search_no_results()
            result = results.select('a')[-1]['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for movie_link in soup.select('div.bolumler a'):
            if 'http' in movie_link['href']:
                video_soup = self.get_soup(movie_link['href'])
                for movie_link in video_soup.select('div.karart iframe'):
                    link = movie_link['src']
                    if 'youtube' in link:
                        continue
                    if 'http' not in link and '/player/' not in link:
                        link = 'http:/'+link
                    if '/player/' in link and '/rad/' not in link:
                        headers = {'Referer':soup._url}
                        link = self.get_redirect_location(self.BASE_URL+link, headers=headers)
                        if not link:
                            video_soup = self.get_soup(self.BASE_URL+movie_link['src'])
                            link = video_soup.select_one('iframe')['src']
                    if '/rad/' in link:
                        video_soup = self.get_soup(self.BASE_URL + movie_link['src'])
                        for link in video_soup.select('div.videoyuver a'):
                            link = link['href']
                    if 'http' not in link:
                        link = 'http://' + link

                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_text=movie_link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

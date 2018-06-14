# coding=utf-8
import re
from sandcrawler.scraper import SimpleScraperBase, ScraperBase
import json
import time

class MovizlandCom(SimpleScraperBase):
    BASE_URL = 'http://movizland.com'
    OTHER_URLS = ['http://vb.movizland.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    USER_AGENT_MOBILE = False
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + search_term

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'الصفحة التالية «')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select_one('div.movies-blocks').find_all('a', text="سيرفرات اضافية")
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        title = None
        for result in results:
            link = result['href']
            title = result.text
            if result.has_attr('title'):
                title = result['title']

            if '/all/' in link or '/tags/' in link or '/account/' in link:
                continue

            if link:
                self.submit_search_result(
                    link_url=link,
                    link_title=title,
                )

    def get(self, url, **kwargs):
        return super(MovizlandCom, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):

        link = soup.find('a', 'RedirecTliNK')
        if link:
            link = link['href']
        else:
            link = soup.select_one('a.ViewMovieNow')
            if link:
                link = link.href


        if link:
            if 'vb.movizland' in link:
                forum_soup = self.get_soup(link)
                movies_links = forum_soup.find_all('a', text=re.compile('Link #'))
                for movies_link in movies_links:
                    movie_soup = self.get_soup(movies_link['href'])
                    source_link = movie_soup.find('a', id='dwn_link')['href']
                    index_page_title = self.util.get_page_title(movie_soup)
                    season, episode = self.util.extract_season_episode(index_page_title)
                    self.submit_parse_result(index_page_title=index_page_title,
                                             series_season=season,
                                             series_episode=episode,
                                             link_url=source_link)


            movie_soup = self.get_soup(link)
            post_data = movie_soup.find('form', attrs={'method':'POST'}).find_all('input')
            data = {}
            for post in post_data:
                data[post['name']] = post['value']
            post_link = movie_soup.find('form', attrs={'method': 'POST'})['action']
            time.sleep(6)


            links_soup = self.post_soup(post_link,data=data)
            index_page_title = self.util.get_page_title(links_soup)
            season, episode = self.util.extract_season_episode(index_page_title)
            source_link = unicode(links_soup).split('sources: [')[-1].split('",')[0]
            source_link = source_link.replace('file:"', '').replace('{', '').replace('}', '')
            urls = self.util.find_urls_in_text(source_link)

            for link in urls:
                if '.m3u8' not in link:
                    self.submit_parse_result(index_page_title=index_page_title,
                                     series_season=season,
                                     series_episode=episode,
                                     link_url=link)

        links = soup.find_all('a', text=re.compile("Link #"))
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in links:
            self.submit_parse_result(index_page_title=index_page_title,
                                     series_season=season,
                                     series_episode=episode,
                                     link_url=link['href'])

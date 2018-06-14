# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class UakinoNet(SimpleScraperBase):
    BASE_URL = 'https://yadoma.tv'
    OTHERS_URLS = ['http://uakino.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _do_search(self, search_term, page=0):
        self.start = page
        self.search_term = search_term
        return self.get(self.BASE_URL + '/search_result.php?ajax=1&search_id={}&offset={}&order=relevance&tag='.format(search_term, page))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self._do_search(search_term).text
        data_text_soup = json.loads(soup)['data'].strip()
        if not data_text_soup:
            return self.submit_search_no_results()
        page = 0
        while self.can_fetch_next():
            if self._parse_search_result(data_text_soup):
                page += 30
                soup = self._do_search(search_term, page).text
                data_text_soup = json.loads(soup)['data'].strip()
            else:
                break

    def _parse_search_result(self, soup):
        if not soup:
            return False
        else:
            json_text_links = self.make_soup(soup).find_all('a', 'heading')
            for json_text_link in json_text_links:
                page_text_link=json_text_link['href']
                title = json_text_link.text.strip()
                self.submit_search_result(
                    link_url=page_text_link,
                    link_title=title,
                )
            return True

    def _parse_parse_page(self, soup):
        title = soup.select_one('meta[property="og:title"]')
        if title:
            title = title['content']
        episodes_links = []
        try:
            episodes_links = soup.find('div', 'media_list_ph').find_all('a', 'thumb')
        except AttributeError:
            pass
        if episodes_links:
            for episodes_link in episodes_links:
                series_season, series_episode = self.util.extract_season_episode(episodes_link['href'])
                ep_soup = self.get_soup(self.BASE_URL+'/'+episodes_link['href'])
                movie_link = ep_soup.find('meta', attrs={'itemprop':'url'})
                if movie_link:
                    movie_link = movie_link['content']
                if not movie_link:
                    movie_link = ep_soup.find('meta', attrs={'property':'og:video'})['content']
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=movie_link,
                    link_text=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        else:
            movie_link = soup.find('meta', attrs={'itemprop': 'url'})['content']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_title=title,
                                     link_url=movie_link)

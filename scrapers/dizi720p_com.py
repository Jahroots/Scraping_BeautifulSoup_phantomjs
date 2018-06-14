# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Dizi720pCom(SimpleScraperBase):
    BASE_URL = 'https://www.dizi720p.co'
    OTHER_URLS = ['http://www.dizi720p.co', 'http://www.dizi720p.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Üzgünüm,hiç içerik eklenmemiş"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', 'navigation_next')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.episodeList article div[class="post_title text-overflow"] a'):
            result = results['href']
            if '/oyuncular/' in result:
                continue
            title = results.text.strip()
            self.submit_search_result(
                link_url=results['href'],
                link_title=results['title'],
                image=self.util.find_image_src_or_none(results, 'img'),
            )
            found = 1

        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.panel-title')
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.filmcik iframe')
        for result in results:
            movie_link = result['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
        for options_links in soup.select('div[class="btn-group alternatives"] ul.dropdown-menu a'):
            options_link =options_links['href']
            if 'http' not in options_link:
                continue
            options_soup = self.get_soup(options_link)
            results = options_soup.select('div.dp_player iframe')
            raw_season = options_soup.select_one('span.season-name')
            if raw_season:
                season=raw_season.text.strip().split()[0]
            raw_episode = options_soup.select_one('span.episode-name')
            if raw_episode:
                episode = raw_episode.text.strip().split()[0]
            for result in results:
                movie_link = result['src']
                if 'http' not in movie_link:
                    movie_link = 'http:'+movie_link
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=movie_link,
                    series_season=season,
                    series_episode=episode,
                )

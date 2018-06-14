# coding=utf-8
import base64
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class KatTv(SimpleScraperBase):
    BASE_URL = 'http://kat.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/search-movies/{search_term}/page-{page}.html'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_results(self, soup):
        if not soup.select('li.item'):
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('li.item'):
            server_link_soup = self.get_soup(result.select_one('a').href)
            for link in server_link_soup.select('p.server_version > a'):
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def save_player(self, soup, index_page_title, title, series_season, series_episode):
        ex = soup.select_one('#player a')
        if ex and ex.href:
            if ex and ex.href:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=ex.href,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        else:
           script =  soup.select_one('#player script')
           if script:
               text = script.text
               split_1 = text.split('Base64.decode("')
               if split_1 and split_1[-1]:
                   split_2 = split_1[-1].split('")')
                   if split_2 and split_2[0]:
                       encoded_link = self.make_soup(base64.decodestring(split_2[0]))
                       iframe = encoded_link.select_one('iframe')

                       if iframe and iframe['src']:
                           self.submit_parse_result(
                               index_page_title=index_page_title,
                               link_url=iframe['src'],
                               link_title=title,
                               series_season=series_season,
                               series_episode=series_episode,
                           )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div#tit_player')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
            title = title.text

        #a#title
        self.save_player(soup, index_page_title, title, series_season, series_episode)

        #servers
        servers = soup.select('p.server_play a')
        if servers:
            for server in servers:
                soup = self.get_soup(server.href)
                self.save_player(soup, index_page_title, title, series_season, series_episode)

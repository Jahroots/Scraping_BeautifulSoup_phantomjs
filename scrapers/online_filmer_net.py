# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class OnlineFilmer(SimpleScraperBase):
    BASE_URL = 'https://online-filmer.org'
    OTHER_URLS = ['http://online-filmer.net', ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    TRELLO_ID = 'Z1SR2Wr9'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'gre'
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'Λυπούμαστε, αλλά δεν υπάρχει.'

    def _fetch_next_button(self, soup):
        link = soup.find('a','nextpostslink')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        for link in soup.select('.movief a'):
            self.submit_search_result(link_url=link['href'],
                                      link_title=link.text
                                      )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.filmborder .filmcontent h1').text
        series_season, series_episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        for option in soup.select('div.filmcontent select option'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=option['value'],
                link_text=option.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        for option in soup.select('div#ap_post_fields div'):
            source_urls = option['value'].decode("hex")
            source_soup = self.make_soup(source_urls)
            url = source_soup.find('iframe')['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_text=option.text,
                series_season=series_season,
                series_episode=series_episode,
            )




                #
        # play_now_btn = soup.select_one('.yazitip a')
        # if play_now_btn:
        #     links = self.util.find_urls_in_text(
        #         self.get(play_now_btn['href']).text)
        #
        #     if links:
        #         for link in links:
        #             if 'advertisingmedia' not in link and \
        #                 'adsmarket' not in link:
        #                 self.submit_parse_result(
        #                     index_page_title=soup.title.text.strip(),
        #                     link_url=link,
        #                     link_text=title,
        #                     series_season=series_season,
        #                     series_episode=series_episode,
        #                 )
        #                 break
        #

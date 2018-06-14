# -*- coding: utf-8 -*-
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class Tvids(SimpleScraperBase):
    BASE_URL = "http://www.tvids.net"
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

            # self.long_parse = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return "No result TV Series or Episodes for"

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('-----------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for serie in soup.select('.rsearch > a'):
            self.submit_search_result(link_title=serie.text,
                                      link_url=self.BASE_URL + '/' + serie.href)
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup, depth=0):

        content = str(soup)
        season, episode = None, None
        # Get the first video
        # onload we do a
        # var idseries="74"; var season="07"; var episode="10"; loadplayer(idseries,season,episode)
        # loadplayer(b,e,a) {$.get(badress+ p_v+ b+"-"+ e+"_"+ a,function(a){$("#cont_player").html(a)})}
        # baddress, p_v are static.


        srch = re.search('var idseries="(.*?)"; var season="(.*)"; var episode="(.*?)"',
                         content)
        if srch:
            season = srch.group(2)
            episode = srch.group(3)
            get_url = self.BASE_URL + '/play/plvids' + \
                      srch.group(1) + '-' + \
                      srch.group(2) + '_' + \
                      srch.group(3)  # a
            vid_soup = self.get_soup(get_url)
            for iframe in vid_soup.select('iframe'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=iframe['src'],
                                         series_season=season,
                                         series_episode=episode
                                         )
        else:
            raise ScraperParseException('Could not find id/series/season in javascript.')

        # Find each of the other videos.
        # ("#morevideo1").click(function(){ morurlvid('DwicBN9mlQbTxr8rLHAIowT7PyUc2Rx8b7ponXdyPy7r44LuQDDFvERQXKQVaZVMl5mTyjtuP2FJMVboBbHd4w,,',this);
        for activation_link in re.findall(
                "morurlvid\('(.*?)',this\)",
                str(soup),
        ):
            new_url = self.BASE_URL + '/play/mvideo_' + activation_link
            link = self.get_redirect_location(new_url)
            if link:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         series_season=season,
                                         series_episode=episode
                                         )

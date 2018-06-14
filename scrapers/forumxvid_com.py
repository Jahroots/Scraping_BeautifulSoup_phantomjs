# -*- coding: utf-8 -*-
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Forumxvid(SimpleScraperBase):
    BASE_URL = 'http://ww12.forumxvid.com'
    OTHERS_URLS = ['http://www.forumxvid.com']
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Website just display ads.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No results found.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next ')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def search(self, search_term, media_type, **extra):

        jsn = json.loads(self.post(self.BASE_URL + '/search/search',
                                   data={'keywords': search_term, 'title_only': '1', 'users': '', 'date': '',
                                         'nodes%5B%5D': '1',
                                         'child_nodes': '1', 'order': 'date', '_xfToken': '',
                                         '_xfRequestUri': '%2Fsearch%2F',
                                         '_xfNoRedirect': '1', '_xfResponseType': 'json'},
                                   headers={'X-Ajax-Referer': 'http://www.forumxvid.com/search/'}).text)
        if jsn.get("message", '') == "No results found.":
            return self.submit_search_no_results()
        if 'error' in jsn:
            raise Exception('SITE MESSAGE: ' + jsn['error'].get('keywords', ''))

        soup = self.get_soup(jsn['_redirectTarget'] + 'c[node]=1+2+3+17+16+15+13+14+4+5+12+7+9+8+10+11+6')

        for link in soup.select('.title a'):
            self.submit_search_result(link_url=link['href'],
                                      link_title=link.text
                                      )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.titleBar h1')
        title = (title.contents[1] if len(title.contents) > 1 else title.text).strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for txt in soup.select('.bbCodeBlock.bbCodeCode pre'):

            for link in self.util.find_urls_in_text(unicode(txt)):

                if not link.startswith(self.BASE_URL) and 'imdb.com/' not in link:

                    if series_season is None:
                        series_season, series_episode = self.util.extract_season_episode(link)

                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_text=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )

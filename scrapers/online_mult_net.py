# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class OnlineMult(SimpleScraperBase):
    BASE_URL = 'http://online-mult.net'
    LONG_SEARCH_RESULT_KEYWORD = '2014'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        self.search_term = search_term
        return self.BASE_URL + '/search/?q={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'По запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return 'http:' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.eTitle a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.eTitle h1').text[9:].strip()
        season, episode = self.util.extract_season_episode(title)

        for iframe in soup.select('iframe'):
            src = iframe.get('src', iframe.get('data-src', None))
            if src and not '/mchat/' in src:
                src = 'http:' + src if src.startswith('//') else src
                if 'online-mylt.ru' in src:
                    soup2 = self.get_soup(src)
                    self._parse_iframes(soup2,
                                        link_title=title,
                                        series_season=season,
                                        series_episode=episode
                                        )
                else:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=src,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

        # series
        for opt in soup.select('.vova option'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=opt['value'],
                                     link_title=title + ' ' + opt.text,
                                     series_season=season,
                                     series_episode=episode
                                     )

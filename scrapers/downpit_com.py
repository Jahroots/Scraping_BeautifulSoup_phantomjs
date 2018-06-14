# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Downpit(SimpleScraperBase):
    BASE_URL = 'http://downpit.com'
    OTHER_URLS = []
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        # raise NotImplementedError('the site doesn\'t function properly' )

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/r.php?s={}&c={}'.format(search_term,
                                                         2 if media_type in (
                                                         self.MEDIA_TYPE_FILM, self.MEDIA_TYPE_TV)
                                                         else '')

    def _parse_search_result_page(self, soup):
        for link in soup.select('.title span a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_no_results_text(self):
        return 'Sorry! the file you are looking for is not found, Please try again.'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('.disp-head > div').text.strip()
        season, episode = self.util.extract_season_episode(title)

        found = False

        for txt in soup.select('.quote') + soup.select('.quote div'):
            for link in txt.contents:

                try:
                    if link and str(link).strip().startswith('http'):
                        if len(link.split('http')) > 2:
                            for url in self.util.find_urls_in_text(link):
                                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                         link_url=url,
                                                         link_title=title,
                                                         series_season=season,
                                                         series_episode=episode
                                                         )
                            found = True
                        else:

                            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                     link_url=link,
                                                     link_title=title,
                                                     series_season=season,
                                                     series_episode=episode
                                                     )
                            found = True
                except Exception as e:

                    self.log.exception(e)

        for link in soup.select('.quote div a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
            found = True

        for link in soup.select('.desc a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
            found = True

        if not found:
            for url in self.util.find_urls_in_text(soup.select_one('#dle-content').text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

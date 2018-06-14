#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class KKisteTo(SimpleScraperBase):

    BASE_URL = 'http://kkiste.to'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "deu"
        raise NotImplementedError('the http://kkiste.to website is not working')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q=' + \
            self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        # Only a lack of results signs no results.
        results = soup.select('li.mbox a')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        # Two ways this is done.
        # Moves just have a link.
        for link in soup.select('li.free a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=link.text,
                                     )
        for link in soup.select('li.premium a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=link.text,
                                     )
        # Or a dropdown of series, POST that to
        # /xhr/movies/episodes/*PAGENAME*/
        # and we get a JSON response with all our episodes.
        # Each episode value shoudl be appended to
        # http://www.ecostream.tv/stream/
        season_select = soup.find('select', 'seasonselect')
        if season_select:
            pagematch = re.search('^%s/(.*)\.html' % self.BASE_URL,
                parse_url)
            if not pagematch:
                raise ScraperParseException(
                    'Could not find name from %s' % parse_url)
            season_url = self.BASE_URL + \
                '/xhr/movies/episodes/' + \
                pagematch.group(1) + \
                '/'
            for season in season_select.select('option'):
                # skip the first one :)
                if not season['value']:
                    continue
                # This will 404 without the X-Requested-With header.
                resp = self.post(
                    season_url,
                    data={'season': season['value']},
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                )
                episodes = resp.json()
                for episode in episodes['episodes']:
                    link_url = 'http://www.ecostream.tv/stream/' + episode['link']
                    self.submit_parse_result(
                                             link_url=link_url,
                                             link_title=episode['part'],
                                             series_season=season['value'],
                                             series_episode=episode['episode']
                                             )



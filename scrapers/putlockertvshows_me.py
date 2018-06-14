# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PutlockerTVshows(SimpleScraperBase):
    BASE_URL = 'http://putlockertvshows.me'
    SINGLE_RESULTS_PAGE = True

    LONG_SEARCH_RESULT_KEYWORD = 'mom'

    def setup(self):
        raise NotImplementedError('Deprecated, website not available')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            for link in mainsoup.select('.lc'):
                lookup[link.text.strip()] = self.BASE_URL + link['href']
                lookup[link.text.lower().strip()] = self.BASE_URL + link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search outselve.s
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        def _ads_redirect(soupy):

            while not [ifr for ifr in soupy.findAll('iframe')
                       if ifr['src'].startswith('http') or 'allowfullscreen' in ifr.attrs]:

                ad_redir = soupy.select_one('.badsvideo')
                if ad_redir:
                    src = ad_redir['onclick'][22:-1]
                    return self.get_soup(self.BASE_URL + src)

                ifr = [fr for fr in soupy.findAll('iframe') if '/ifr/' in fr['src']]
                if ifr:
                    src = ifr[0]['src']
                    soupy = self.get_soup(self.BASE_URL + src)

            return soupy

        title = soup.select('.fc td')[0].text.strip()

        for link in soup.select('.fc .la'):
            season, episode = self.util.extract_season_episode(link['href'].split('/')[-1])

            soup_ = _ads_redirect(self.get_soup(self.BASE_URL + link['href']))

            for fr in soup_.findAll('iframe'):
                if fr['src'].startswith('http') or 'allowfullscreen' in fr.attrs:
                    vid_link = self.BASE_URL+'/'.join(fr['src'].split('/')[:-1])+'/vid/'+fr['src'].split('/')[-1]
                    movie_url = self.get_soup(vid_link).select_one('iframe')
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=movie_url['src'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

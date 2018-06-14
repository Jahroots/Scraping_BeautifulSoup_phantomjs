# -*- coding: utf-8 -*-
import string
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class TVshowsHDTV(SimpleScraperBase):
    BASE_URL = 'http://tvshows-hdtv.org'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'walking dead'

    DAYS_TO_PARSE = 3660

    lookup = None

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self._request_size_limit = (1024 * 1024 * 10)  # Bytes

        self._request_connect_timeout = 500
        self._request_response_timeout = 500

    def get(self, url, **kwargs):
        kwargs['allowed_errors_codes'] = [404, ]
        return super(TVshowsHDTV, self).get(url, **kwargs)


    @cacheable(expire=60*60*24)  # 24h
    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {} if self.lookup is None else self.lookup

        for page in xrange(self.DAYS_TO_PARSE - 1):
            if not page:  # 1st
                soup = self.get_soup(self.BASE_URL)
            else:
                next_page_link = soup.find('img', src="i/icon_older_posts.jpg")
                self.log.debug('---------- {} ---------'.format(page))
                if next_page_link:
                    soup = self.get_soup(self.BASE_URL + '/' + next_page_link.parent.href)
                else:
                    break

            for show_name in soup.select('td > span > center'):
                try:
                    tr_with_links = list(show_name.parent.parent.parent.next_siblings)[1]

                    show_name = show_name.text.strip().replace('.', ' ')
                    lookup[show_name] = dict(site_page=soup._url,
                                             parsed_links=[a.href for a in tr_with_links.select('a')])
                except:
                    pass
                    # lookup[show_name.upper()] = link['href']
        return lookup

    def __buildlookup_CAPTCHA(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each(
                [self.BASE_URL + '/downloads_{}.html'.format(letter) for letter in '0' + string.lowercase]):
            # TODO below this
            for link in mainsoup.select('.ddmcc ul ul li a'):
                lookup[link.text.strip()] = link['href']
                lookup[link.text.lower().strip()] = link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search ourselves
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term) or re.search(search_term, term, re.IGNORECASE):
                self.submit_search_result(
                    link_url=page['site_page'],
                    link_title=term,
                )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        lookup = self.__buildlookup()
        for term, page in lookup.items():
            if page['site_page'] == parse_url:
                season, episode = self.util.extract_season_episode(term)
                for url in page['parsed_links']:
                    if not url.startswith(self.BASE_URL):
                        self.submit_parse_result(index_page_title=self.get_soup(parse_url).title.text.strip(),
                                                 link_url=url,
                                                 link_title=term,
                                                 series_season=season,
                                                 series_episode=episode
                                                 )

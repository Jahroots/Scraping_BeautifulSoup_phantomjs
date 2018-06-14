# coding=utf-8

from sandcrawler.scraper import PHPBBSimpleScraperBase
from sandcrawler.scraper import ScraperBase


class ForodeSeries(PHPBBSimpleScraperBase):
    BASE_URL = 'http://forodeseries.net'

    SINGLE_RESULTS_PAGE = True

    FORUMS = -1

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL + '/search.php?mode=results',
            data={
                'search_keywords': search_term,
                'search_terms': 'all',
                'search_author': '',
                'search_forum': self.FORUMS,
                'search_time': 0,
                'search_fields': 'titleonly',
                'sort_by': 0,
                'sort_dir': 'DESC',
                'show_results': 'topics',
                'return_chars': 200
            },
            headers={'Origin': self.BASE_URL,
                     'Accept-Encoding': 'gzip, deflate',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Referer': self.BASE_URL + '/search.php',
                     'User-Agent': self.USER_AGENT,
                     })

    def search(self, search_term, media_type, **extra):
        # self._login()
        self.get(self.BASE_URL + '/search.php')
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.topictitle a'):
            found = True
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
            )
        if not found:
            self.submit_search_no_results()

    def parse(self, page_url, **kwargs):
        # self._login()
        super(PHPBBSimpleScraperBase, self).parse(page_url, **kwargs)

    def _parse_parse_page(self, soup):
        title = soup.select_one('.maintitle').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.postlink')+soup.select('.postbody a'):
            if not 'mail' in link.href:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

        for box in soup.select('.code'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )
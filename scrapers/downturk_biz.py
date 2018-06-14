# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DownTurkBiz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.downturk.net'

    OTHER_URLS = ['http://www.downturk.net']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u"La recherche n'a retourné aucun résultat."

    def _parse_search_result_page(self, soup):
        rslts = soup.select('div.post-title > h3 > a')
        if not rslts:
            self.submit_search_no_results()

        for result in rslts:

            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        # Looks like hand generated, but seems to have the rule that links
        # are in a <div class="quote"
        # Grab that, and text within, split on newline and check for a http
        page_title = soup.select('div.post-title > h3')[0].text
        season, episode = self.util.extract_season_episode(page_title)
        for result in soup.select('div.quote'):
            for line in result.strings:
                if line.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=line,
                                             series_season=season,
                                             series_episode=episode,
                                             )

# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TopSerialyCz(SimpleScraperBase):
    BASE_URL = 'http://topserialy.cz'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'No standard web pages containing all your search terms were found.'

    def setup(self):
        raise NotImplementedError('Website Not Available.')

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'next »')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        for link in soup.select('h2.entry-title a'):
             self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        iframes = soup.select('.entry-content iframe')
        for iframe in iframes:
            title = self.util.get_page_title(soup)
            season, episode = self.util.extract_season_episode(title)
            url = iframe['src']
            self.submit_parse_result(index_page_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     link_url=url)

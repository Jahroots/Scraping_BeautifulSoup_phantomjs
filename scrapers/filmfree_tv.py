# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmFreeTv(SimpleScraperBase):
    BASE_URL = 'http://filmfree.tv'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ita'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'It looks like nothing was found at this location'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.next.page-numbers')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('.entry-title a')

        if not results:
            self.submit_search_no_results()

        for link in results:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        image = self.util.find_image_src_or_none(soup, 'div.entry-content img')
        for iframe in soup.select('div.entry-content iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     )

        for link in soup.select('div.entry-content a'):
            season, episode = self.util.extract_season_episode(
                unicode(link.parent.contents[0]))
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=link.text,
                                     image=image,
                                     series_season=season,
                                     series_episode=episode
                                     )

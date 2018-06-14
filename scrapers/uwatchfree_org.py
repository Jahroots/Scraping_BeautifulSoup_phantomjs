# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, SimpleGoogleScraperBase, EmbeddedGoogleScraperBase


class UwatchfreeOrg(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'https://www.uwatchfree.tv'
    OTHER_URLS = ['https://www.uwatchfree.to', 'https://www.uwatchfree.co', 'http://www.uwatchfree.co', 'http://www.uwatchfree.me', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        results = soup.select('div.table-responsive table tbody tr a')
        for result in results:
            movie_link = result['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
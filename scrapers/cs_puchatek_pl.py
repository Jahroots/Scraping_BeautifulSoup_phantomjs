# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class CS_Puchatek(SimpleScraperBase):
    BASE_URL = "http://cs-puchatek.pl"

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "pol"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Niestety - brak wyników.'

    def _fetch_next_button(self, soup):
        links = soup.select('span.prev_next a')
        for link in links:
            if link.find('img', {'alt': 'Następny'}):
                return self.BASE_URL + '/' + link['href']
        return None

    def search(self, search_term, media_type, **extra):
        # self.get(self.BASE_URL)
        self._parse_search_results(
            self.post_soup(self.BASE_URL + '/search.php?do=process',
                           data={'titleonly': 1,
                                 'securitytoken': 'guest',
                                 'do': 'process',
                                 'query': search_term,
                                 'B1': '',
                                 }
                           )
        )

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3.searchtitle a'):
            (season, episode) = self.util.extract_season_episode(result.text)
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                series_season=season,
                series_episode=episode,
            )

    def _parse_parse_page(self, soup):
        title = (soup.select_one('.title.icon') or soup.select_one('.threadtitle')).text.strip()
        season, episode = self.util.extract_season_episode(title)

        for item in soup.select('.bbcode_code'):
            for link in self.util.find_urls_in_text(item.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

        for link in soup.select('.postcontent.restore div a'):
            if link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

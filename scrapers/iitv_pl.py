# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class IitvPl(SimpleScraperBase):
    BASE_URL = 'http://iitvx.pl/'
    OTHER_URLS = ['http://iitv.pl/']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'second chance'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def post(self, url, **kwargs):
        return super(IitvPl, self).post(url,  allowed_errors_codes=[403], **kwargs)

    def get(self, url, **kwargs):
        return super(IitvPl, self).get(url, allowed_errors_codes=[403], **kwargs)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/szukaj',
                data={'text': search_term,
                      }
            )
        )

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('a.ellipsis'):
            link = result['href']
            season, episode = self.util.extract_season_episode(link)
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                series_season=season,
                series_episode=episode
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('div#player iframe'):
            movie_link = link['src']
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=movie_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )

        links = soup.select('a.direct-link-button')
        for link in links:
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link.href,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
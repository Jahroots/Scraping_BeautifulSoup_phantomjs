# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class OnlainFilmiNet(SimpleScraperBase):
    BASE_URL = 'http://onlainfilm.club'
    OTHER_URLS = ['https://onlain-filmi.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'bul'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'a6GpLvR1'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Sorry, no posts matched your criteria'

    def _fetch_next_button(self, soup):
        #next_button = soup.find('li', id='navigation-next').find('a')
        #if next_button:
        #    return next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        search_url = 'http://onlainfilm.club/load/'
        soup = self.post_soup(search_url, data= {'query': search_term, 'a': 2})
        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('div.content-middle a.fv-left')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
                self.submit_search_result(
                    link_url=result.href,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('iframe#film_main'):
            src = link['src']
            if 'http' not in src:
                src = 'http:' + src
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
            )

        results = soup.select('div.vk_multifilm option')
        for result in results:
            src = result['value']
            if 'http' not in src:
                src = 'http:' + src
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=link.text,
            )

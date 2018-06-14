# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Jomvphd2Com(SimpleScraperBase):
    BASE_URL = 'https://www.jomvphd2.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Sorry, but you do not have film'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.moviefilm'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div[align="center"] iframe'):
            if 'youtube' in result['src']:
                continue
            link_soup = self.get_soup(result['src'])
            links = self.util.find_urls_in_text(link_soup.find_all('script')[-1].text)
            for link in links:
                if 'usercontent' in link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=result.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

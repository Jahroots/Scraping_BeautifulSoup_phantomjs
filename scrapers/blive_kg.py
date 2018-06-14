# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class BliveKg(SimpleScraperBase):
    BASE_URL = 'http://www.blive.kg'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL,
            data={
                'S':search_term})

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u' >> ')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.vcell1'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('script'):
            link = re.search("""addVariable\("file","(.*)\"\)""", result.text)
            if link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.group(1),
                    link_title=link.group(1),
                    series_season=series_season,
                    series_episode=series_episode,
                )

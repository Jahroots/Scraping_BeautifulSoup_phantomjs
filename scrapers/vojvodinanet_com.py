# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re

class VojvodinanetCom(SimpleScraperBase):
    BASE_URL = 'https://www.vojvodinanet.com'
    OTHER_URLS = ['http://www.vojvodinanet.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hrv'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/search/?q={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Results 0-0 of 0'

    def _fetch_next_button(self, soup):
        next_button = soup.find('span', text='»')
        if next_button:
            return 'http:' + next_button.parent.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('article.entry')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img', prefix=self.BASE_URL),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe in soup.select('div.video-wrapper iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                series_season=series_season,
                series_episode=series_episode,
            )
        for link in re.findall('\{link:"(.*?)"', unicode(soup)):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                series_season=series_season,
                series_episode=series_episode,
            )


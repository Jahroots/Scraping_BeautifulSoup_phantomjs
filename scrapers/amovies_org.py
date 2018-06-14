# -*- coding: utf-8 -*-
import re
from urlparse import urlparse, urljoin
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AmoviesOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://amovies.cc'
    OTHER_URLS = ['http://amovies.biz', 'http://amovies.org','http://amovies.ws']
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'не найдено ни одного материала'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a[id="film"]')+soup.select('a[id="serials"]'):
            link = self.get_redirect_location(result.href)
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        if '/serials/' in soup._url:
            for iframe_link in soup.select('div#vk_if iframe'):
                film_id = None
                try:
                    film_id =iframe_link['id']
                except KeyError:
                    pass
                if film_id:
                    movie_links = soup.select('select[id="series"] option')
                    for movie_link in movie_links:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=movie_link['value'],
                            link_text=movie_link['value'],
                            series_season=series_season,
                            series_episode=series_episode,
                        )
                else:
                    headers = {'Referer': soup._url}
                    source = iframe_link['src']
                    source_headers = {'Referer': source}
                    series_urls_text = self.get_soup(self.get_soup(source, headers=headers).select_one('iframe')['src'], headers = source_headers).text.split('uvk.show')[-1]
                    iframe_link = self.get_soup(source, headers=headers).select_one('iframe')['src']
                    parsed_url = urlparse(iframe_link)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
                    series_urls = re.findall("""["](.*?)["]""", series_urls_text)
                    for series_url in series_urls:
                        movie_link = urljoin(domain,series_url)
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=movie_link,
                            link_text=movie_link,
                            series_season=series_season,
                            series_episode=series_episode,
                        )
        else:
            link = soup.select_one('div.viboom-overroll iframe')
            if link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_text=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

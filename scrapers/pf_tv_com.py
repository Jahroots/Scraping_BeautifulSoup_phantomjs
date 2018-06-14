#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PftvCom(SimpleScraperBase):

    BASE_URL = 'http://putlocker9.ws'
    OTHER_URLS = ['http://putlocker.cz', 'http://putlockermovies.ch', 'http://putlockerhd.in', 'http://putlocker4k.be', 'http://www.pf-tv.com', 'http://pf-tv.com']
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_no_results_text(self):
        return "Nothing found"


    def _fetch_next_button(self, soup):
        return None

    def _fetch_search_url(self, search_term, media_type=None):
            self.search_term = search_term
            return self.BASE_URL + '/results.php?term={}'.format(search_term)

    def _do_search(self, search_term):
        for m_type in self.MEDIA_TYPES:
            links = self._fetch_search_url(search_term, media_type=m_type)
            return self.get_soup(links)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        movie_links = soup.select('div.item')
        if not movie_links:
            self.submit_search_no_results()
        for result in movie_links:
            link = result.select_one('a')
            if '/tv-show/' in soup._url:
                episode_links_soup = self.get_soup(link)
                episode_links = episode_links_soup.select('div.episode a')
                for episode_link in episode_links:
                    self.submit_search_result(
                        link_url=episode_link.href,
                        link_title=episode_link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
            else:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in soup.select('div.table-scroll a[href*="videolink"]'):
            self.log.debug(link.href)

            movie_link_soup = self.get_soup(link.href)
            movie_link = movie_link_soup.select_one('div[class="row watch-buttons"] a[class="btn btn-blue white"]').href
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=movie_link,
                                     series_season=season,
                                     series_episode=episode
                                     )


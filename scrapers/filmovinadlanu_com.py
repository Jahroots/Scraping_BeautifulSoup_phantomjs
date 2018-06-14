# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmovinadlanuCom(SimpleScraperBase):
    BASE_URL = 'http://www.ludaksite.net'
    OTHER_URLS = ['http://filmovinadlanu.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cro'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/page/{page}/?s={search_term}'.format(base_url=self.BASE_URL,
                                                                                     search_term=search_term,
                                                                                     page=page)
    def setup(self):
        raise NotImplementedError('Deprecated. Website not providing any results.')

    def _fetch_next_button(self, soup):
        return None

    def _fetch_no_results_text(self):
        return u'No content available'


    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        episode_titles = soup.select('div.episodiotitle a')
        if episode_titles:
            for episode_title_url in episode_titles:
                episode_soup = self.get_soup(episode_title_url['href'])
                link_title = episode_title_url['href'].split('-')[-1]
                series_season, series_episode = link_title.split('x')
                iframe_link = episode_soup.select_one('div.embed2 iframe')
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link['src'],
                    link_title=iframe_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        else:
            for link in soup.select('div.movieplay iframe'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        # script_links = soup.select('div.movie_bottom_info div.tab script')
        # for script_link in script_links:
        #     if 'file' in script_link.text:
        #         for movie_link in self.util.find_urls_in_text(script_link.text):
        #             self.submit_parse_result(
        #                 index_page_title=index_page_title,
        #                 link_url=movie_link,
        #                 link_title=movie_link,
        #                 series_season=series_season,
        #                 series_episode=series_episode,
        #             )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class NontonfilmId(SimpleScraperBase):
    BASE_URL = 'http://nontonfilm.id'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ind'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Website not available')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'NO POSTS FOUND'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.animelistest'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.player-embed iframe'):
            link_url = link['src']
            if 'http' not in link_url:
                link_url = 'http:'+link_url
            link_title = link.text
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link_url,
                link_title=link_title,
                series_season=series_season,
                series_episode=series_episode,
            )
        for mirror_link in soup.find('div', 'mirrorcon').find_all('a', href=True):
            mirror_soup = self.get_soup(soup._url+mirror_link['href'])
            for link in mirror_soup.select('div.player-embed iframe'):
                link_url = link['src']
                if 'http' not in link_url:
                    link_url = 'http:' + link_url
                link_title = link.text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link_title,
                    series_season=series_season,
                    series_episode=series_episode,
                )

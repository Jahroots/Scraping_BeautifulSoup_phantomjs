# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ShostreamFr(SimpleScraperBase):
    BASE_URL = 'http://www.shostream.fr'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/phpajax/recherche.php?q={search_term}&f=name&display=1'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def setup(self):
        raise NotImplementedError('Deprecated. Connection Timeout')

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('li'):
            link = result.select_one('a.searchResultsLink')
            if link:
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
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for regarder_link in soup.select('a[rel="linkbox"]'):
            regarder_soup = self.get_soup(self.BASE_URL+regarder_link.href)
            ajax_link = unicode(regarder_soup).split("facebox({ajax: '")[-1].split("'});")[0]
            result_soup = self.get_soup(self.BASE_URL+'/'+ajax_link)
            for link in result_soup.select('a.replaceFrame'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
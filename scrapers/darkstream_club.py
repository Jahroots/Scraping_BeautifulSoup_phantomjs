# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DarkstreamClub(SimpleScraperBase):
    BASE_URL = 'http://www.darkstream.club'
    OTHER_URLS = ['http://darkstream.biz']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Website not Available')


    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Non è stato trovato nulla'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.art-post h2.art-postheader'):
            link = result.select_one('a')
            if link:
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
        tables_links = soup.select('div[align="center"] table tr')
        for tables_link in tables_links:
            links = tables_link.find_all('td', attrs={'width':'300'})+tables_link.find_all('td', attrs={'width':'306'})+\
                    tables_link.find_all('td', attrs={'width':'302'})
            for link in links:
                download_links = link.find_all('a')
                for download_link in download_links:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=download_link.href,
                        link_title=download_link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

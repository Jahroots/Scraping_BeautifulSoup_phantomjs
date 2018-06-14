# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class OranlineCom(SimpleScraperBase):
    BASE_URL = 'http://www.vixto.net'
    OTHER_URLS = ['http://www.oranline.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/buscar?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        results = soup.select('#all div.row figure')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a')

            if 'peliculas' in link.href:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
            elif 'series' in link.href:
                series_soup = self.get_soup(link.href)
                seasons = series_soup.select('div[class="details-block seasons"] a')
                for season in seasons:
                    soup = self.get_soup(season.href)
                    episodes = soup.select('h4.media-heading a')
                    for episode in episodes:
                        self.submit_search_result(
                            link_url=episode.href,
                            link_title=episode.text,
                            image=self.util.find_image_src_or_none(result, 'img'),
                        )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for link in soup.select('div.tab-pane iframe'):
            #link = links.select_one('a')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )

        table = soup.select('#linkslistonline td a[title="Reproducir"]')
        for link in table:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )


        table = soup.select('#linkslistdownload td a[title="Descargar"]')
        for link in table:
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
            )
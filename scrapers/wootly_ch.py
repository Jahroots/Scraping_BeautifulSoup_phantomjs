# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WootlyCh(SimpleScraperBase):
    BASE_URL = 'http://www.levidia.ch'#'http://www.wootly.ch'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Website moved to levidia.')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?q={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('li.mlist'):
            link = link.select_one('a')
            found = True
            soup = self.get_soup(self.BASE_URL + '/' + link.href)
            for s in soup.select('li[class="mlist links"] a'):
                season, episode = self.util.extract_season_episode(link.text)

                self.submit_search_result(
                    link_url= self.BASE_URL + '/' + s['href'],
                    link_title=link.text,
                    series_season=season,
                    series_episode=episode
                )
        if not found:
            self.submit_search_no_results()

    def parse(self, page_url, **kwargs):
        soup = self.get_soup(page_url)
        title = soup.select_one('h1')
        if title and title.text:
            title = title.text
        season, episode = self.util.extract_season_episode(title)

        links = soup.select('ul.mfeed li a')
        for link in links:
            if link.href.find('gateway'):
                soup = self.get_soup(link.href)
                link = soup.select_one('a[href*="direct"]')
                if link:
                    soup = self.get_soup(self.BASE_URL + '/' + link.href)
                    iframe = soup.select_one('iframe')
                    self.submit_parse_result(
                                             index_page_title= self.util.get_page_title(soup),
                                             link_url=iframe['src'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
            else:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link.href,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )

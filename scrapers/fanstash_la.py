# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FanstashLa(SimpleScraperBase):
    BASE_URL = 'https://fanstash.net'
    OTHER_URLS = ['http://fanstash.se']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/tvshows-{}/Page1.html'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"No tvshows results"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'›')
        return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('ul.new_episodes h4 a'):
            result = results['href']
            ser_soup = self.get_soup(result)
            ser_links = ser_soup.select('ul.seasons_list ul a')
            title = ser_soup.select_one('h1').text
            for ser_link in ser_links:
                link_title = title+' '+ser_link.text.strip()
                season, episode = self.util.extract_season_episode(ser_link['href'])
                self.submit_search_result(
                    link_url=ser_link['href'],
                    link_title=link_title,
                    series_season=season,
                    series_episode=episode,
                )
                found = 1
            if not found:
                return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        results = soup.select('div#linkholder tbody tr')
        for result in results:
            movie_link = result.find_all('td')[2].find('a')['href']
            if 'fanstash.se' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= self.BASE_URL + movie_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
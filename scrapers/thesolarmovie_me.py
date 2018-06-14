# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class ThesolarmovieMe(SimpleScraperBase):
    BASE_URL = 'https://putlockeris.org'
    OTHER_URLS = 'http://thesolarmoviehd.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Deprecated, Internal Sever error')


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nu am gasit ce cautai,incearca din nou'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.index_container div[class="index_item index_item_ie"]'):
            results = results.select_one('a')
            title = results.text
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        for link in soup.select('table.dataTable td.entry2 a[rel="nofollow"]'):
            movie_link = link['href'].split('url=')[-1]
            if 'http' not in movie_link or 'primewire' in movie_link:
                continue
            movie_link = link['href'].split('url=')[-1]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                series_season=season,
                series_episode=episode,
                link_text=title,
            )

class ProjectfreetvSc(ThesolarmovieMe):
    BASE_URL = 'https://putlockeris.org'
    OTHER_URLS = ['http://www.projectfreetvseries.org']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

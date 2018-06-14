
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TvShowsOnline(SimpleScraperBase):
    BASE_URL = 'http://www.7stream.pro/'
    OTHER_URLS = ['http://tv-showsonline.com', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        raise NotImplementedError('the website returns the bad gateway error')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s='+ '%s' % self.util.quote(search_term)


    def _fetch_no_results_text(self):
        return 'No Articles Found'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        self.log.debug(link)
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.item_content h4 a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url = result['href'],
                link_title = result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[class="entry_title entry-title"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        titles = soup.select('span.ser-name')
        index = 0
        for link in soup.select('a.wo-btn'):
            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url=link['href'],
                link_title=titles[index].text,
                series_season=season,
                series_episode=episode
            )
            index += 1

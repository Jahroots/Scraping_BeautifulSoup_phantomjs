# coding=utf-8
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class Final4Ever(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.final4ever.com'

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):

        raise NotImplementedError('Site no longer available.')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/tags.php?tag=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'No content has been tagged with'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('-' * 30)
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in [a for a in soup.select('a') if 'id' in a.attrs and a['id'].startswith('thread_title_')]:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('td.navbar').strong.text.strip()
        season, episode = self.util.extract_season_episode(title)

        for box in soup.select('.alt2'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )

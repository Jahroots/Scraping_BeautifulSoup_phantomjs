# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class AracinemaCo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://aracinema.co'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'Oo7b1p0i'

    def setup(self):
        super(self.__class__, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def perform_action(self):
        action_url = self._get_cloudflare_action_url()
        self.log.info('Fetching %s for Cloudflare cookies.', action_url)
        wd = self.webdriver()
        wd.get(action_url)
        tries = 0
        while tries < self.cloudflare_tries():
            tries += 1
            # Check for a flagged value.
            if 'data-translate="checking_browser"' in wd.page_source:
                self.log.info(
                    'Cloudflare browser check still present after %s tries... '
                    'sleeping.', tries)
                time.sleep(self.cloudflare_wait())
            # elif 'recaptcha' in wd.page_source:
            #     self.log.info('Found recaptcha on page; attempting to solve.')
            #     self.solve_recaptcha()
            #     break
            else:
                self.log.info('Passed CF browser check!')
                break

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search criteriag'

    def _fetch_next_button(self, soup):
        next_link = ''
        try:
            next_link = soup.find('a', text=u'»')['href']
        except TypeError:
            pass
        return next_link if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('a.first_A'):
            result = results['href']
            title = results.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found = 1
        if not found:
           return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        results = soup.find_all('div', 'wpb_tab ui-tabs-panel wpb_ui-tabs-hide vc_clearfix')
        for result in results:
            iframe_link = result.find('iframe')['src']
            if 'youtube' in iframe_link:
                continue

            if iframe_link.find('http') == -1:
                iframe_link = 'http:' + iframe_link

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe_link,
                link_text=title,
                series_season=season,
                series_episode=episode,
            )
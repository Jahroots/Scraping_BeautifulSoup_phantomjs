# -*- coding: utf-8 -*-
import base64
import re

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class Watchtvseries_unblocked_pe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://watchtvseries.unblckd.gdn'
    OTHER_URLS = ['http://watchtvseries.unblckd.cc', 'http://watchtvseries.unblckd.bz', 'http://watchtvseries.unblckd.bet', 'http://watchtvseries.unblckd.cam','http://watchtvseries.unblckd.vip', 'http://watchtvseries.unblckd.biz',
                  'http://watchtvseries.unblckd.ws', 'http://watchtvseries.unblckd.one',
                  'https://watchtvseries.unblocked.pe', 'https://watchtvseries.unblocked.uno',
                  'http://watchtvseries.unblckd.bid']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    LONG_PARSE = True
    TRELLO_ID = 'tAwgxsGh'
    WEBDRIVER_TYPE = 'phantomjs'
    REQUIRES_WEBDRIVER = True

    def _get_cloudflare_action_url(self):
        return  'https://watchseries.unblocked.mx/search/man'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' › ')
        return self.BASE_URL + link['href'] if link else None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[403, 404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return 'Sorry we do not have any results for that search'

    def _parse_search_result_page(self, soup):
        results = soup.select('div a.poster')
        if not results and len(results) == 0 and 'page' not in soup._url:
            return self.submit_search_no_results()

        for result in results:
            #result = result.parent
            show_soup = self.get_soup(self.BASE_URL + result['href'])
            for epis_link in show_soup.select('.listings.show-listings a'):
                num_links_search = re.search('\((\d+) links\)', epis_link.text)
                if num_links_search:
                    num_links = int(num_links_search.group(1))
                    if num_links == 0:
                        self.log.info('0 links listed on %s - not submitting',
                                      epis_link.href)
                        continue
                    else:
                        self.log.debug('%s links listed on %s - submitting',
                            num_links, epis_link.href)
                else:
                    self.log.warning('Could not find num links on %s', result['href'])
                self.submit_search_result(
                    link_url=epis_link.href,
                    link_title=epis_link.text,
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.channel-title')
        sea = None
        episode = None

        if title:
            title = title.text[5:-8].strip()
            self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)

        for a in soup.select('#myTable a.watchlink'):

            if not a.has_attr('title'):
                continue

            if 'Sponsored' in a['title']:
                continue
            if 'cale.html' in a['href']:
                base = a['href'].split('=')[1].strip()
                try:
                    base = base64.urlsafe_b64decode(base)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=base,
                        link_title=title,
                        series_season=sea,
                        series_episode=episode
                    )
                except Exception as e:
                   self.log.warning(str(e))

            else:
                dload_soup = self.get_soup(a['href'])
                link = dload_soup.select_one('.myButton')['href']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=title,
                    series_season=sea,
                    series_episode=episode
                    )

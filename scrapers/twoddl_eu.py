# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TwoDdl(SimpleScraperBase):
    BASE_URL = 'http://2ddl.io'
    OTHER_URLS = [
        'http://tddl.tv',
        'http://iiddl.net',
        'http://twoddl.co',
        'http://2ddl.pro',
        'http://2ddl.download',
        'http://2ddl.la'
        'http://iiddl.com',
        'http://2ddl.cc',
        'http://2ddl.co',
        'http://2ddl.to',
        'http://twoddl.eu',
        'http://2ddl.net',
        'http://2ddl.ag',
        'http://2ddl.io',
        'http://2ddl.org',
        'http://2ddl.link'
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(TwoDdl, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('.posttitle h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.posttitle > h2 > a').text
        seas, epis = self.util.extract_season_episode(title)

        for link in soup.select('.postarea > p > a'):
            href = link['href']
            # if href.startswith('http://track.globaltrackads.com'):
            #     href = self.get(href, verify=False).url  # http HEAD doent work here

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=href,
                                     link_title=title,
                                     series_season=seas,
                                     series_episode=epis,
                                     )

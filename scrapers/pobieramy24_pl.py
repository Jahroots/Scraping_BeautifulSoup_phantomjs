# -*- coding: utf-8 -*-
import time
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException
from sandcrawler.scraper.extras import VBulletinMixin
import re



class Pobieramy24(VBulletinMixin, SimpleScraperBase):
    BASE_URL = 'http://pobieramy24.pl'

    USERNAME = 'victoraruffin'
    PASSWORD = 'pilemap4windowhoyts'
    # USERNAME = 'kikko'
    # PASSWORD = 'qikko'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'pol'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _login_success_string(self):
        return 'kujemy za zalogowanie'

    def _fetch_no_results_text(self):
        return u'Niestety - brak wyników'

    #The search now is a pop up with all records in a single view without pagination.
    def _fetch_next_button(self, soup):

        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else None

    def search(self, search_term, media_type, **extra):

        """if not hasattr(self, 'depth'):
            self.depth = 1
        else:
            self.depth += 1
        if self.depth > 5:
            raise ScraperParseException(
                'reached depth of 5 trying to login.')
        """

        self.search_term = search_term
        self.media_type = media_type

        self.get(self.BASE_URL)
        self._login()

        home_soup = self.get_soup(self.BASE_URL)
        security_token = home_soup.find('input', {'name': 'securitytoken'})
        if security_token:
            security_token = security_token['value']
        else:
            m = re.search(u'(SECURITYTOKEN = ).*";', home_soup.text)
            security_token = m.group(0).replace('SECURITYTOKEN = ', '').replace('"', '').replace(';', '')

        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data={'securitytoken': security_token,
                      'do': 'process',
                      'q': search_term, })
        )

    def _parse_search_result_page(self, soup):

        # To forum wymaga odczekania 5 sekund pomiędzy wyszukiwaniami. Spróbuj ponownie za 3 sekund.
        if 'To forum wymaga odczekania' in str(soup):
            self.log.warning('waiting...')
            time.sleep(int(str(soup).split('Spróbuj ponownie za ')[1].split(' sekund')[0]) + .33)
            return self.search(self.search_term, self.media_type)

        results = soup.select('a[id*="thread_title"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for link in results:

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)



    def parse(self, parse_url, **extra):
        self.get(self.BASE_URL)
        self._login()
        soup = self.get_soup(parse_url)

        for box in soup.select('.bbcode_code'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=soup.title.text,
                                         #series_season=series_season,
                                         #series_episode=series_episode,
                                         )

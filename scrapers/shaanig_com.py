# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Shaanig(SimpleScraperBase):
    BASE_URL = 'https://www.shaanig.org'
    OTHER_URLS = ['http://www.shaanig.com']
    SINGLE_RESULTS_PAGE = True

    # USERNAME = 'Forrosiver'
    # PASSWORD = 'Eipai1sae'

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    # SECURITY_TOKEN_NAME = 'securitytoken'

    # ALLOW_GUEST_TOKEN = False

    def setup(self):
        raise NotImplementedError('Deprecated. Website has shutdown permanently')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def X_login_post_data(self):
        md5_password = self._md5password()
        login_data = {
            'vb_login_username': self.USERNAME,
            'vb_login_password': '',
            'vb_login_password_hint': '',
            'securitytoken': self._get_security_token(),
            'cookieuser': '1',
            's': '',
            'do': 'login',
            'vb_login_md5password': md5_password,
            'vb_login_md5password_utf': md5_password,
        }
        return login_data

    def _fetch_no_results_text(self):
        return 'Sorry - no matches.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else  None

    def search(self, search_term, media_type, **extra):
        # self.get(self.BASE_URL)
        # self._login()
        home_soup = self.get_soup(self.BASE_URL)
        # security_token = home_soup.find(
        #     'input', {'name': 'securitytoken'})['value']
        self._parse_search_results(

            self.post_soup(self.BASE_URL + '/ajaxlivesearch.php?do=search',
                           # Xdata={'do': 'search', 'lsawithword': 1, ',allforum': '', 'securitytoken': 'guest',                                 's': '', 'lsasort': 'lastpost', 'lsasorttype': 'DESC', 'keyword': search_term,},
                           data='&do=search&lsawithword=1&,allforum&lsasort=lastpost&lsasorttype=DESC&keyword={}&securitytoken=guest&s='.format(
                               search_term),
                           headers={'X-Requested-With': 'XMLHttpRequest',
                                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        )

    def _parse_search_result_page(self, soup):
        results = [a for a in soup.select('lsagroup ajaxlivesearch > ol > li > a') if 'title' in a.attrs]
        if not results:
            self.submit_search_no_results()

        for link in results:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)

        for post in soup.select_one('#posts'):
            for link in self.util.find_urls_in_text(unicode(post), skip_images=True):
                if 'shaanig.' not in link and 'imdb' not in link and '/extraimago.com' not in link:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_text=soup.h1.text.strip()
                                             )

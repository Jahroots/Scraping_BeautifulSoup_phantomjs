# -*- coding: utf-8 -*-

import hashlib
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class KapeCc(SimpleScraperBase):
    BASE_URL = 'http://kape.cc'
    OTHER_URLS = []
    USERNAME = 'Everned'
    PASSWORD = 'eo0aJei6'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL)

        if u'Привет,' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            self.post(self.BASE_URL,
                                     data={'login':'submit', 'login_name':username, 'login_password':PASSWORD
                                            }
                                     )

    def _fetch_next_button(self, soup):
        link = soup.find('a', rel="next")
        return self.BASE_URL + '/' + link['href'] if link else  None

    def search(self, search_term, media_type, **extra):
        self._login()
        home_soup = self.get_soup(self.BASE_URL+'/index.php?do=search&subaction=search&story={}&search_start=1'.format(search_term))
        self._parse_search_results(home_soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(
            u'К сожалению, поиск по сайту не дал никаких результатов') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('div.news_body a'):
            img = result.select_one('img')
            title = result.text
            if img:
                title = img['title']
            if u'подробнее' in result.text:
                self.submit_search_result(
                    link_url=result.href,
                    link_title=title
                )
        next_link = soup.select_one('img[alt="next"]')
        if next_link:
            next_link = next_link.find_previous('a')
            if next_link and self.can_fetch_next():
                self._parse_search_results(self.get_soup(
                    next_link['href']
                ))

    @cacheable()
    def _follow_link_repeat(self, link):
        while '/get/' in link:
            if not link.startswith('http'):
                link = u'{}{}'.format(self.BASE_URL, link)
            link = self.get_redirect_location(link)
        return link

    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        for post in soup.select('div.news_body a'):
            if '/get/' in post.href:
                link = self._follow_link_repeat(post.href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                )

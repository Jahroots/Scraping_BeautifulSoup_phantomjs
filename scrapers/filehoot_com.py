# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileHoot(SimpleScraperBase):
    BASE_URL = 'http://filehoot.com'
    USER_LOGIN = 'Camir1935'
    PASSWORD = 'aeze0jo8Lie'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise NotImplementedError('the domain is expired')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _login(self):
        page = self.post(self.BASE_URL + '/login.html',
                         data=dict(op='login', redirect='', login=self.USER_LOGIN, password=self.PASSWORD)).content
        if 'Incorrect Login or Password' in page:
            raise Exception('Incorrect Login or Password')

    def search(self, search_term, media_type, **extra):
        self._login()

        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?k={}&op=catalogue'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next »')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('.table.table-striped.table-condensed tr > td > a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):

        title = soup.title.text.replace('Watch ', '').replace('- FileHoot', '').replace('online', '').strip()
        season, episode = self.util.extract_season_episode(title)

        page = self.post(soup._url, data=dict(
            op='download1',
            usr_login='',
            id=soup._url[20:-5],
            fname='',
            referer=self.BASE_URL + '/?op=catalogue&k=&ftype=&fsize_logic=gt&fsize=',
            method_free='Continue to watch your Video')).content

        try:
            url = page.split('file: "')[1].split('",')[0]

            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=url,
                link_title=title,
                series_season=season,
                series_episode=episode
            )
        except Exception as ee:
            self.log.exception(ee)

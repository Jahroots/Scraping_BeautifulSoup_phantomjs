# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class VidwatchMe(SimpleScraperBase):
    BASE_URL = 'http://vidwatch.me'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_NAME = 'Conise'
    PASSWORD = 'pohngaiX7'
    EMAIl = 'paulakraft@teleworm.us'

    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):

        # if media_type == self.MEDIA_TYPE_FILM:
        #     return self.BASE_URL + '/?op=search&k=' + self.util.quote(search_term) + '&user=&tag=&cat_id=1'
        # elif media_type == self.MEDIA_TYPE_TV:
            return self.BASE_URL + '/?op=search&k=' + self.util.quote(search_term) + '&user=&tag=&cat_id='

    def _fetch_no_results_text(self):
        return u' TODO '

    def _fetch_next_button(self, soup):
        return None

    def _login(self):
        soup = self.post_soup(self.BASE_URL+'/login.html', data = {'op' : 'login',
                                                     'redirect' :'',
                                                     'login' : self.USER_NAME,
                                                      'password' : self.PASSWORD}
                              )

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.get_soup(self._fetch_search_url(self.util.quote(search_term),  media_type))
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.videobox a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('div.videobox'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )


    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        id =  soup.select_one('input[name="id"]')['value']
        fname = soup.select_one('input[name="fname"]')['value']
        referer= soup.select_one('input[name="referer"]')['value']
        hash = soup.select_one('input[name="hash"]')['value']

        soup = self.post_soup(parse_url, data = {'op' : 'download1',
                                                 'usr_login' : '',
                                                 'id' : id,
                                                 'fname' : fname,
                                                 'referer' : referer,
                                                 'hash' : hash,
                                                 'imhuman' : 'Proceed to video'}
        )

        self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('textarea iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )

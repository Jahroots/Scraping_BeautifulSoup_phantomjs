# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, \
    CachedCookieSessionsMixin, ScraperAuthException

class CopiapopCom(SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'http://copiapop.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'mother'

    USERNAME = 'Theeng1941'
    EMAIL = 'NicoleDChandler@armyspy.com'
    PASSWORD = 'muevahH8ti'

    def setup(self):
        raise NotImplementedError('Website Not available')

    def _fetch_no_results_text(self):
        return u'No hay resultados'

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                '{}/action/SearchFiles'.format(self.BASE_URL),
                data={
                    'Phrase': search_term
                }
            )
        )

    def _fetch_next_button(self, soup):
        # Note - pagination doesn't work on the site, but this is how
        # it 'should' work.
        next_button = soup.select_one('div.tiles_container li.pageSplitter')
        if next_button and next_button.get('data-nextpage-url'):
            return '{}{}'.format(
                self.BASE_URL, next_button.get('data-nextpage-url'))
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.tiles_container li h2.name'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url='{}{}'.format(self.BASE_URL, link.href),
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        return super(CopiapopCom, self).parse(parse_url, **extra)

    def _login(self, token):

        soup = self.post_soup(
            '{}/action/Account/Login'.format(self.BASE_URL),
            data = {
                'UserName': self.USERNAME,
                'Password': self.PASSWORD,
                '__RequestVerificationToken': token,
            }
        )

        if soup.select('div.auth_list'):
            raise ScraperAuthException('Failed login')

        self.save_session_cookies()


    def _parse_parse_page(self, soup):
        if soup.select('div.auth_list'):
            # We have the 'signin' thingie on the top right.
            # Go signin
            token = soup.select_one('input[name="__RequestVerificationToken"]')['value']
            self._login(token)
            soup = self.get_soup(soup._url)


        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(index_page_title)

        # First get the preview
        for video_block in soup.select('div#fileDetails'):
            url = video_block.get('data-player-file')
            if url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    series_season=series_season,
                    series_episode=series_episode,
                )

        # Now extract the 'real video'
        form = soup.select_one('form.download_form')
        if form:
            data = {}
            for input in form.select('input'):
                name = input.get('name')
                value = input.get('value')
                if name and value:
                    data[name] = value
            response = self.post(
                '{}{}'.format(self.BASE_URL, form['action']),
                data=data
            ).json()
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url='{}{}'.format(self.BASE_URL, response['DownloadUrl']),
                series_season=series_season,
                series_episode=series_episode,
            )



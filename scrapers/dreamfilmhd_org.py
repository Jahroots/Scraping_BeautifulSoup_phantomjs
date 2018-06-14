# coding=utf-8

import base64
import re
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class DreamFilmHdOrg(SimpleScraperBase):
    BASE_URL = 'http://dreamfilmhd.tv'
    OTHER_URLS = ['http://dreamfilmhd.io', 'https://dreamfilmhd.info', 'http://dreamfilmhd.sh', 'https://dreamfilmhd.io']
    TRELLO_ID = 'WNfk1rNo'

    def get(self, url, **kwargs):
        return super(DreamFilmHdOrg, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "dan"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.proxy_region = 'nl'  # at least not US!

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        soup = self._need2sleep(soup)
        link = soup.find('a', text='Next »')
        self.log.debug('---------------')
        if link:
            return link['href']

    def _fetch_search_url(self, search_term, media_type):
        self.search_term = search_term
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _need2sleep(self, soup):
        if 'You need to wait ' in str(soup):
            self.log.debug('sleeping...')
            time.sleep(int(str(soup).split('You need to wait ')[1].split(' second')[0]) + 1.33)
            return self.get_soup(soup._url)
        else:
            return soup

    def _parse_search_result_page(self, soup):
        soup = self._need2sleep(soup)

        results = soup.select('div.movie-poster')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            link = result.select_one('a')

            image = self.util.find_image_src_or_none(
                result, 'img')
            if image and not image.startswith('http'):
                image = self.BASE_URL + '/' + image
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image
            )

    def __decode(self, data):
        return self.util.unquote(base64.b64decode(data))
        # return data

    def __fetch_tv(self, seasons):
        # Fetch the URL
        for season in seasons:
            series_season = self.util.find_numeric(season['id'])
            for episode in season.select('a.episode'):
                series_episode = self.util.find_numeric(episode.text)
                # $ Note - this is fully confident of a result.
                response = self.post(
                    self.BASE_URL + '/CMS/modules/series/ajax.php',
                    data={
                        'action': 'showmovie',
                        'id': episode['rel']
                    }

                )
                content_soup = self.make_soup(
                    self.__decode(
                        response.json()['url']
                    )
                )
                self._parse_iframes(
                    content_soup,
                    series_episode=series_episode,
                    series_sesason=series_season,
                    asset_type=ScraperBase.MEDIA_TYPE_TV,

                )

    def __fetch_movie(self, soup):
        # We have a base64 encoded string.
        # javascript: function a {unescape(atob(data)) }
        # document.write(a('....'))
        movie_box = soup.select('div#m0 script')
        if not movie_box:
            raise ScraperParseException('Failed to find movie box')
        movie_box = movie_box[0]
        search = re.search("document.write\(a\('([^']*)'\)\)", movie_box.text)
        if search:
            data = search.group(1)
            # Make soup out of that and extract iframes :D
            content_soup = self.make_soup(self.__decode(data))
            self._parse_iframes(
                content_soup,
                asset_type=ScraperBase.MEDIA_TYPE_FILM

            )

    def _parse_parse_page(self, soup):
        # Do we have div.season?
        """seasons = soup.select('div.season')
        if seasons:
            self.__fetch_tv(seasons)
        else:
            self.__fetch_movie(soup)
        """
        iframes = soup.select('#postContent')

        self._parse_iframes(soup)



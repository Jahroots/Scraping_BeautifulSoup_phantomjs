# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CachedCookieSessionsMixin
from string import uppercase
from sandcrawler.scraper.caching import cacheable
import re



class StreamlordCom(CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.streamlord.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_FILM,
        ScraperBase.MEDIA_TYPE_TV
    ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_NAME = 'Entle1955'
    PASSWORD = 'ea2ieM1ch'
    EMAIL = 'gertruderjennings@armyspy.com'
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'IMztJkUg'

    def get(self, url, **kwargs):
        return super(StreamlordCom, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def setup(self):
        super(StreamlordCom, self).setup()
        self._request_connect_timeout = 600
        self._request_response_timeout = 600

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.post_soup('http://www.streamlord.com/searchapi2.php', data = {'searchapi2' : search_term})
        results = soup.select('div[class="item movie"] a[href*=".html"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.log.debug(result.href)
            if result and len(result.href) > 1:
                self.submit_search_result(
                    link_url=result.href,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )


    def _login(self):
        soup = self.post_soup('http://www.streamlord.com/login.html', data = {'username' : self.USER_NAME,
                                                                            'password': self.PASSWORD,
                                                                            'submit' : 'Login'})
        self.save_session_cookies()

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        title = soup.select_one('div.movie-title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        found_results = False
        for result in re.findall('return\("(http://.*?)"', unicode(soup)):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=result,
                series_season=season,
                series_episode=episode,

            )
            found_results = True

        for iframe in soup.select('div#movielist iframe'):
            result = iframe.get('src')
            if result:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result,
                    series_season=season,
                    series_episode=episode,

                )
                found_results = True

        if not found_results:
            # Use jwplayer object to pull out the parsed results
            # (There's some obvuscation around them...)
            self.webdriver().get(parse_url)
            for result in self.webdriver().execute_script(
                """
                var results = []
                jwplayer('container').config.playlist.forEach(function(pl) {
                    pl.sources.forEach(function(source) {
                        results.push(source.file)
                    })
                })
                return results
                """
            ):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result,
                    series_season=season,
                    series_episode=episode,

                )

# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin


class Live2hustle(VBulletinMixin, SimpleScraperBase):
    BASE_URL = 'https://live2hustle.life'
    OTHER_URLS = ['http://www.live2hustle.net']

    LONG_SEARCH_RESULT_KEYWORD = 'The'
    SINGLE_RESULTS_PAGE = True
    USERNAME = 'Befoodly'
    PASSWORD = 'Ebo4che9j'


    # 'CharlesGMacias@armyspy.com'


    def setup(self):
        raise NotImplementedError('Deprecated.Website no longer have relevants results.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def __buildlookup(self):  # lookup
        MOVIES_FORUM_URL = self.BASE_URL + '/fam/forumdisplay.php/42-MOVIES/page{}'

        movie_to_url = {}
        page = 1
        while True:
            soup = self.get_soup(MOVIES_FORUM_URL.format(page))
            for thrd in soup.select('.threadtitle')[2:]:
                if 'Sticky:' not in thrd.text:
                    movie_to_url[thrd.text.strip()] = thrd.a.href
            if (not self.can_fetch_next()) or \
                page == 20 or (page > 1 and len(soup.select('.first_last')) < 4):
                break
            page += 1

        return movie_to_url

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search ourselves
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                self.submit_search_result(
                    link_url=self.BASE_URL + '/fam/' + page,
                    link_title=term,
                )
                any_results = True
        if not any_results:
            self.submit_search_no_results()


    # def _fetch_no_results_text(self):
    #     return 'No content has been tagged with'
    #
    # def _fetch_next_button(self, soup):
    #     link = soup.find('a', text='>')
    #     self.log.debug('-' * 30)
    #     return self.BASE_URL + '/' + link['href'] if link else None
    #
    # def _parse_search_result_page(self, soup):
    #     for result in [a for a in soup.select('a') if 'id' in a.attrs and a['id'].startswith('thread_title_')]:
    #         self.submit_search_result(
    #             link_url=result['href'],
    #             link_title=result.text
    #         )

    def _parse_parse_page(self, soup, count=0):
        try:
            title = soup.select_one('.title.icon').text.strip()
        except AttributeError as e:
            # vBulletin Message
            # It appears that you've exceeded the maximum number of posts you can view, but wait, there's a simple solution.
            # To unlock the forum and continue viewing messages, all you need to do is sign up for a free account. The entire process takes just a few minutes so create your account now and view as many threads as you like!
            # self._login()
            self.log.warning(e)
            # time.sleep(3)
            # TODO   we need proxy rotator or Tor to catch all links
            self._http_session = None
            count += 1
            if count == 5:
                raise e
            return self._parse_parse_page(self.get_soup(soup._url), count)

        season, episode = self.util.extract_season_episode(title)

        for url in soup.select('.postcontent.restore a'):
            if url.href.startswith('http'):

                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )

        for box in soup.select('.alt2'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )

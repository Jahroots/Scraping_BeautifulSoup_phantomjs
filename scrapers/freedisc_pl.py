# -*- coding: utf-8 -*-
import json
import re
from sandcrawler.scraper.caching import cacheable
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin, DuckDuckGo


class FreeDisc(DuckDuckGo, AntiCaptchaMixin, SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'https://freedisc.pl'
    OTHERS_URLS = ['http://freedisc.pl']
    SINGLE_RESULTS_PAGE = True
    RECAPKEY = '6LdQexoTAAAAAIjiXgE5D6VDsItC8AHhEzh1KqHz'
    USER_AGENT_MOBILE = False


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'pol'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, *args, **kwargs):
        try:
            return super(FreeDisc, self).get(*args, **kwargs)
        except Exception, e:
            # If it was a search error, try and solve the recap then try again.
            if e.message in ('Fetch error.  Check url/site availability.', 'Gone'):
                self._submit_captcha_solve()
                return super(FreeDisc, self).post(*args, **kwargs)
            raise


    def post(self, *args, **kwargs):
        try:
            return super(FreeDisc, self).post(*args, **kwargs)
        except Exception, e:
            # If it was a search error, try and solve the recap then try again.
            if e.message in ('Fetch error.  Check url/site availability.', 'Gone'):
                self._submit_captcha_solve()
                return super(FreeDisc, self).post(*args, **kwargs)
            raise

    def _submit_captcha_solve(self):
        self.post_soup(
            self.BASE_URL,
            data={
                'g-recaptcha-response': self.get_recaptcha_token()
            }
        )
        self.save_session_cookies()

    # def search(self, search_term, media_type, **extra):
    #     self.load_session_cookies()
    #     response = self.post(
    #         self.BASE_URL + '/search/get',
    #         data='{"search_phrase":"%s","search_type":"movies","search_saved":0,"pages":2,"limit":150}' % search_term,
    #         headers={
    #             'Referer': self.BASE_URL,
    #             'X-Requested-With': 'XMLHttpRequest',
    #             'Content-Type': 'application/json'
    #         },
    #
    #     )
    #     jsn = json.loads(response.text)
    #
    #     uid2name = jsn["response"]["logins_translated"]
    #
    #     found = False
    #
    #     for film in jsn["response"]["data_files"]['data']:
    #         self.submit_search_result(
    #             # http://freedisc.pl/DagMarta,f-3991394,star-trek-tas-18-bem-avi
    #             link_url=self.BASE_URL + "/{user},f-{filmid},{filmslug}".format(
    #                 user=uid2name[str(film['user_id'])]["userLogin"],
    #                 filmid=film['id'],
    #                 filmslug=film['name_url']),
    #             link_title=film['name']
    #         )
    #         found = True
    #
    #     if not found:
    #         self.submit_search_no_results()

    @cacheable()
    def _extract_parse_results(self, parse_url):
        soup = self.get_soup(
            parse_url,
        )
        page_title = self.util.get_page_title(soup)

        title = soup.select_one('h1.padding-5')
        season, episode = None, None
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)
        results = []
        for vidsource in soup.findAll('link', attrs={'rel': "video_src"}):

            filename = vidsource['href']
            if 'file=' in filename:
                filename = filename[filename.find('file=') + 5:]
                results.append(dict(
                    index_page_title=page_title,
                    link_url=filename,
                    series_season=season,
                    series_episode=episode
                    ))
        return results

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        for result in self._extract_parse_results(parse_url):
            self.submit_parse_result(
                **result
            )

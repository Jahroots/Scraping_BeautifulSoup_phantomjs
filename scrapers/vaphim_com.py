# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable

class VaphimCom(AntiCaptchaMixin,CachedCookieSessionsMixin,  SimpleScraperBase):
    BASE_URL = 'https://vaphim.com'
    OTHER_URLS = ['http://vaphim.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    RECAPKEY = "6LcxkiUUAAAAAPb-Lj2CtCvAXjPJwiiTlglennBj"
    RECAPURL = BASE_URL
    DOWNLOAD_URL = BASE_URL +  '/wp-content/themes/moview/unsecure-request/download-response.php'



    def _fetch_no_results_text(self):
        return u'Xin lỗi, chúng tôi không thể tìm thấy bất kỳ kết quả dựa trên truy vấn tìm kiếm của bạn'

    def _fetch_search_url(self, search_term, media_type, n=1):
        self.n = n
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/?s={}'.format(search_term)

        # return self.BASE_URL + '/?searchtype=movie&post_type=movie&s={}'.format(search_term)

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        if link:
            return link.href
        else:
            return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.movie-poster'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    @cacheable()
    def _extract_link(self, url):
        self.load_session_cookies()
        soup = self.get_soup(url)
        if soup.select('div.g-recaptcha'):
            # we need to solve a recap.
            soup = self.post_soup(
                self.DOWNLOAD_URL,
                data={
                    'g-recaptcha-response': self.get_recaptcha_token(),
                    'post_ID' : soup.select_one('#post_ID')['value']
                }
            )

            self.save_session_cookies()
            #return the download urls already
        return list(soup.select('div.tab-content a'))

    def _parse_parse_page(self, soup):
        self.load_session_cookies()
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        id_num = soup.select_one('input#post_ID')
        if id_num:
            id_num = id_num['value']
            post_link = soup.select_one('div.moview-details button')['data-url']
            post_soup = self.post_soup(post_link, data={'post_ID':id_num})
            movie_link = post_soup.select_one('div#WEB-DL a')
            short_link = post_soup.select_one('div#Thu-muc-HOT a')
            if short_link:
                short_link = short_link['href']
            else:
                short_link = ''
            if movie_link:
                movie_link = movie_link['href']
                movie_links = [movie_link, short_link]
                for link in movie_links:
                    if link:
                        self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link,
                                link_title=link,
                                series_season=series_season,
                                series_episode=series_episode,
                        )

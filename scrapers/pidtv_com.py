# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PidtvCom(SimpleScraperBase):
    BASE_URL = 'http://pidtv.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError('Not available')

    def post(self, url, **kwargs):
        return super(PidtvCom, self).post(url,  allowed_errors_codes=[404], **kwargs)

    def get(self, url, **kwargs):
        return super(PidtvCom, self).get(url, allowed_errors_codes=[404], **kwargs)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/wp-admin/admin-ajax.php',
                data={'action':'ajaxsearchpro_search',
                      'aspp':search_term,
                      'asid':'1',
                      'asp_inst_id':'1_1',
                      'options':'qtranslate_lang=0&set_intitle=None&customset%5B%5D=post'
                }
            )
        )

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('a.asp_res_url'):
            link = result['href']
            if '/imdb/' in link:
                continue
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1').text.strip()
        for link in soup.select('a.abutton'):
            if '/imdb/' in link:
                continue
            movie_links = self.util.find_file_in_js(self.get_soup(link['href']).text)
            for movie_link in movie_links:
                if '/sub/' in movie_link:
                    continue
                if movie_link:
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=movie_link,
                        link_text=title,
                    )
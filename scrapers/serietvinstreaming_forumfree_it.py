# coding=utf-8
import time
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.extras import VBulletinMixin


class SerietvinstreamingForumfreeIt(SimpleScraperBase):
    BASE_URL = 'http://serietvinstreaming.forumfree.it'

    LONG_SEARCH_RESULT_KEYWORD = 'The'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
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

    def get(self, url, **kwargs):
        return super(SerietvinstreamingForumfreeIt, self).get(url, allowed_errors_codes=[404], **kwargs)

    def __buildlookup(self):
        forum_list_soup = self.get_soup('http://serietvinstreaming.forumfree.it/')
        forum_li_links = forum_list_soup.find('li', id='c64590460').find('ul', 'big_list').find_all('li', 'off plate')
        movie_to_url = {}
        for forum_li_link in forum_li_links:
            forum_link = forum_li_link.find('h3').find('a')['href']
            movie_link_soup = self.get_soup(forum_link)
            big_list_forum = ''
            try:
                big_list_forum = movie_link_soup.find('ul', 'big_list').find('h3', 'web').find('a')['href']
            except AttributeError:
                pass
            if big_list_forum:
                movie_link_soup = self.get_soup(big_list_forum)
            navigation_lis = []
            try:
                navigation_lis = movie_link_soup.find('div', 'navsub top Justify').find_all('li')[2:]
            except AttributeError:
                pass
            if navigation_lis:
                for navigation_li in navigation_lis:
                    navigation_link = navigation_li.find('a')['href']
                    movie_link_soup = self.get_soup(navigation_link)
                    links_ols = movie_link_soup.find('ol', 'big_list').find_all('h3', 'web')
                    for links_ol in links_ols:
                        movie_to_url[links_ol.text.strip()] = links_ol.a.href
            else:
                links_ols = movie_link_soup.find('ol', 'big_list').find_all('h3', 'web')
                for links_ol in links_ols:
                    movie_to_url[links_ol.text.strip()] = links_ol.a.href
        return movie_to_url

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.find('h2', 'mtitle').text
        for url in soup.select('div.mainbg ol.List tr.center a'):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url.href,
                                         link_title=title,
                                         )


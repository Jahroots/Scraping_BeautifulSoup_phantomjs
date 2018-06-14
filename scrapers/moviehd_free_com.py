# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class MoviehdFreeCom(SimpleScraperBase):
    BASE_URL = 'https://www.moviehd-free.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tha'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'ขออภัย. ไม่พบบทความที่ท่านค้นหา'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        if link:
           return link['href']

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('div.movief a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        movie_links = soup.select('div.video-wraper iframe')
        for movie_link in movie_links:
            link = movie_link['src']
            if 'youtube' in link:
                continue
            if 'http' not in link:
                link = 'http:'+link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_text=title,
            )

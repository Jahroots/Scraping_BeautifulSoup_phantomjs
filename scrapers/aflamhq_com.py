# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class AflamhqCom(SimpleScraperBase):
    BASE_URL = 'http://www.aflamhq.co'
    OTHER_URLS = [
        'http://forums.aflamhq.com',
        'http://forums.aflamhq.co',
        'http://www.forums.aflamhq.com',
        'http://www.forums.aflamhq.co',
        'http://www.aflamhq.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return  u'{}/tag/{}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'لا يوجد نتائج ليتم عرضه'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'التالي')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.content ul li'):
            result = results.find('a')['href']
            forum_soup = self.get_soup(result)
            refresh_url = forum_soup.find('meta', attrs={'http-equiv':'refresh'})['content'].split('URL=')[-1]
            if 'adf.ly' in refresh_url:
                continue
            title = results.find('a').text
            self.submit_search_result(
                link_url=refresh_url,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    @cacheable()
    def _follow_link(self, url):
        movie_soup = self.get_soup(url)
        movie_link = movie_soup.select_one('a#downloadlink')
        if movie_link:
            return [movie_link.href, ]
        return []


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div#ayoub a')
        for result in results:
            if 'http' in result.text and 'adyou.me' not in result['href']:
                link = result['href']
                for result in self._follow_link(link):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=result,
                        link_text=title,
                    )

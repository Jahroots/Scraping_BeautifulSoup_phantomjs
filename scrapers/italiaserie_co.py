# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class ItaliaserieCo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.italiaserie.blue'
    OTHER_URLS = ['http://www.italiaserie.co', 'http://www.serietvu.com' ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Risultati della ricerca per"

    def _parse_search_results(self, soup):
        found = 0
        for results in soup.select('div.post-thumb'):
            link = results.select_one('a')['href']
            if link:
                title = results.text.strip()
                self.submit_search_result(
                    link_url=link,
                    link_title=title,
                    image=self.util.find_image_src_or_none(results, 'img'),
                )
                found = 1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div[class="su-spoiler-content su-clearfix"] a')
        for result in results:
            movie_link = result['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )

class ItaliaserieNews(ItaliaserieCo):
    BASE_URL = 'http://www.serietvu.com'
    OTHER_URLS = ['http://www.italiaserie.news', 'http://www.italiaserie.click']

    def setup(self):
        raise NotImplementedError('The website is deprecated')

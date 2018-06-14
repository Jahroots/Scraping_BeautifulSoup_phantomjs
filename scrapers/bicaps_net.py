# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class BicapsNet(SimpleScraperBase):
    BASE_URL = 'http://www.bicaps.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Üzgünüz, kriterlerinize uygun film yok.'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('div.moviefilm a'):
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
        index_page_title = self.util.get_page_title(soup)
        for movie_link in soup.select('div.keremiya_part a'):
            if 'http' in movie_link['href']:
                video_soup = self.get_soup(movie_link['href'])
                for movie_link in video_soup.select('div.filmicerik iframe'):
                    link = movie_link['src']
                    if 'http' not in link:
                        link = 'http:'+link
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_text=movie_link.text,
                    )


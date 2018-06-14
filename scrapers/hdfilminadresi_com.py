# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class HdfilminadresiCom(SimpleScraperBase):
    BASE_URL = 'http://www.hdfilminadresi.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        raise NotImplementedError("Website changed it's content")

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('article.article div.article-container-alt a'):
            title = results.text
            result = results['href']
            download_soup = self.get_soup(result)
            for download_link in download_soup.select('div#sayfalama a'):
                self.submit_search_result(
                    link_url=download_link['href'],
                    link_title=title
                )
                found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div#kendisi iframe')
        for result in results:
            movie_link = result['src']
            if 'okruu.php' in movie_link:
                movie_link = self.get_soup(movie_link).find('iframe')
                if movie_link:
                    movie_link = movie_link['src']
                else:
                    continue

                if 'http' not in movie_link:
                    movie_link = 'http:'+movie_link
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_text=title,
                    )
            elif 'hdf_player' in movie_link:
                movie_links = json.loads(self.get_soup(movie_link).text.split('sources :')[-1].split('],')[0]+']')
                for movie_link in movie_links:
                    movie_link = movie_link['file']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_text=title,
                    )
            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )

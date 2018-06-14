# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PeliculasaudiolatinoCom(SimpleScraperBase):
    BASE_URL = 'http://peliculasaudiolatino.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/autoplete.php',
                data={
                    'search':search_term,
                }
            )
        )

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('div#show a'):
            link = result['href']
            title = result.find_next('div', id='conteresult').text.strip()
            self.submit_search_result(
                link_url=link,
                link_title=title,

            )
            found = 1
        if not found:
            return self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1.titulopeli').text.strip()
        for result in soup.select('div#btnp a'):
            encoded_link = None
            try:
                encoded_link = result['onclick'].split("('")[-1].split("',")[0]
            except KeyError:
                pass
            if encoded_link:
                iframe_soup = self.get_soup(encoded_link)
                iframe_encoded = iframe_soup.find('iframe')
                if iframe_encoded:
                    iframe_encoded = iframe_encoded['src']
                    if 'tinyurl' in iframe_encoded:
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=iframe_encoded,
                                                 link_title=title
                                                 )
                    else:
                        referer = soup._url
                        if 'http' in iframe_encoded:
                            movie_soup = self.get_soup(iframe_encoded, headers={'Referer':referer})
                            movie_link = ''
                            try:
                                movie_link = movie_soup.find('iframe')['src']
                            except TypeError:
                                pass
                            if movie_link:
                                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                         link_url=movie_link,
                                                         link_title=title
                                                         )
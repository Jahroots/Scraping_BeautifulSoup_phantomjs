# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class NontonMobi(SimpleScraperBase):
    BASE_URL = 'http://www.nonton.mobi'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(NontonMobi, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Lainnya atau dapat menggunakan arsip di bawah'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next')
        return self.BASE_URL + next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.select('div.item a')
        any_results = False
        for block in blocks:
            link = block['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1[itemprop="name"]').text

        iframes = soup.select('div.movieplay iframe')
        for iframe in iframes:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                link_title=title
            )

        series = soup.select('div.nonton_part a')
        for ep_link in series:
            ep_link = ep_link['href']
            series_soup = self.get_soup(ep_link)
            movie_links = series_soup.select('div.filmicerik iframe')
            for movie_link in movie_links:
                movie_link = movie_link['src']
                if 'youtube' in movie_link:
                    continue
                self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=movie_link,
                                link_title=title
                            )
        movie_links = soup.select('div.filmicerik iframe')
        for movie_link in movie_links:
            movie_link = movie_link['src']
            if 'http:' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=title
            )

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin
from sandcrawler.scraper.caching import cacheable

class TugaflixCom(SimpleScraperBase, AntiCaptchaMixin):
    BASE_URL = 'https://www.tugaflix.com'
    OTHER_URLS = ['http://tugaflix.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    RECAPKEY = '6Ld2nhcUAAAAAAMhYrTNGaplsFFsPmc71nkKQSTv'

    def _fetch_search_url(self, search_term, media_type):
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            return '{}/Series?G=&O=1&T={}'.format(self.BASE_URL, self.util.quote(search_term))
        # Default to movie search.
        return '{}/Filmes?G=&O=1&T={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Não foram encontrados resultados!'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Seguinte »')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.browse-movie-wrap'):
            link = result.select_one('a')
            url = '{}{}'.format(self.BASE_URL, link.href)
            if link.href.startswith('/Serie'):
                # Need to fetch episodes.
                series_soup = self.get_soup(url)
                for episode in series_soup.select('a.browse-movie-link'):
                    self.submit_search_result(
                        link_url='{}{}'.format(self.BASE_URL, episode.href),
                        link_title=episode.text,
                        image=self.util.find_image_src_or_none(result, 'img', prefix=self.BASE_URL),
                    )
            else:
                self.submit_search_result(
                    link_url=url,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img', prefix=self.BASE_URL),
                )

    @cacheable()
    def _extract_parse_results(self, parse_url):

        soup = self.post_soup(
            parse_url,
            data ={
                'g-recaptcha-response': self.get_recaptcha_token()
            }
        )
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.episode')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(
                title.text)
        results = []
        for iframe in soup.select('iframe'):
            results.append(dict(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                series_season=series_season,
                series_episode=series_episode,
            ))
        return results


    def parse(self, parse_url, **extra):

        for result in self._extract_parse_results(parse_url):
            self.submit_parse_result(
                **result
            )
        soup = self.get_soup(parse_url)
        links_done = set([parse_url, ])
        for serverlink in soup.select('a.btnserv'):
            url = u'{}{}'.format(self.BASE_URL, serverlink.href)
            if url not in links_done:
                links_done.add(url)
                for result in self._extract_parse_results(url):
                    self.submit_parse_result(
                        **result
                    )




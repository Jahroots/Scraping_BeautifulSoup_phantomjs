# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class StreamingClicTv(SimpleScraperBase):
    BASE_URL = 'http://streamingclic.top'

    OTHER_URLS = ['http://www.streamingclic.top', 'http://www.streamingclic.info', 'http://www.istreamin.com','http://www.streamingclic.net', ]

    #LONG_SEARCH_RESULT_KEYWORD = 'mother'

    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'N6fgEXR6'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(StreamingClicTv, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def _fetch_no_results_text(self):
        return 'XXX ne correspond aux termes de recherche'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' >> ')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.item-container div.item a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            if 'http' not in link['href']:
                link_url = self.BASE_URL + '/' + link['href']
            else:
                link_url = link['href']

            if 'facebook' in link_url or 'films-lang' in link_url:
                continue

            link_title = result.text

            image = None
            if result.img:
                image = result.img.get('src')

            if 'serie' in link_url:
                soup = self.get_soup(link_url)
                links = soup.select('td.epi_choix a')
                for link in links:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link_title,
                        image= image
                    )

            else:
                self.submit_search_result(
                    link_url=link_url,
                    link_title=link_title,
                    image=image
                )


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        if 'episode' in soup._url:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_text=title,
                                     link_url=soup.select_one('span[id*="link"]').text
                                     )
        else:

            links = soup.select('#download-button a') + soup.select('#streaming-hd a')
            for link in links:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                    link_text=title,
                                    link_url=link.href
                                    )


class StreamingClicFilm(StreamingClicTv):

    def setup(self):
        raise NotImplementedError('Duplicate of StreamingClicTv')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/recherche.php?q=' + \
               self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        if not soup.select('div.unfilm'):
            self.submit_search_no_results()
            return
        super(StreamingClicFilm, self)._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        self._extract_video_page(soup)

# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class HdfullTv(SimpleScraperBase):
    BASE_URL = 'https://hdfull.tv'
    OTHER_URLS = ['http://hdfull.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'srICXV5G'

    def setup(self):
        super(self.__class__, self).setup()
        self.requires_webdriver = ('parse',)
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar'

    def _fetch_no_results_text(self):
        return u'Desafortunadamente no hemos podido encontrar nada relacionado con su búsqueda'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):

        soup = self.get_soup(self.BASE_URL)
        magic = soup.select_one('input[name="__csrf_magic"]')['value']

        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {
            '__csrf_magic': magic,
            'menu' : 'search',
            'query': search_term
        })

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.item a')

        if not results and len(results) == 0:
            return self.submit_search_no_results()
        
        for result in soup.select('div.item'):
            link = result.select_one('a')
            if 'pelicula' in link.href:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
            else:
                aux_soup = self.get_soup(link.href)
                links = aux_soup.select('div.container a[itemprop="url"]')
                for a in links:
                    aux_soup = self.get_soup(a.href)

                    urls = aux_soup.select('div[itemprop="partOfSeries"] a[href*="temporada"]')
                    for u in urls:
                        if 'Especiales' in u.text:
                            continue

                        self.submit_search_result(
                                    link_url=u.href,
                                    link_title=link.text,
                                    image=self.util.find_image_src_or_none(result, 'img'),
                        )

    def _phantom_get_soup(self, url):
        self.webdriver().get(url)
        return self.make_soup(self.webdriver().page_source)

    @cacheable()
    def _extract_link(self, url):
        soup = self._phantom_get_soup(u'{}{}'.format(self.BASE_URL, url))
        follow_link = soup.select_one('#external-link')
        return follow_link.href

    def _get_links(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(
                title.text)

        for link in soup.select('#embed-list ul li a'):
            if link.href:
                link_url = self._extract_link(link.href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

    def parse(self, parse_url, **extra):

        soup = self._phantom_get_soup(parse_url)

        if 'pelicula' in parse_url:
            self._get_links(soup)
        else:
            for episode in soup.select('a.spec-border-ie'):
                soup = self._phantom_get_soup(episode.href)
                self._get_links(soup)

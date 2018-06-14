# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, \
    AntiCaptchaMixin, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable

class DdlIslandSu(SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin):
    BASE_URL = 'http://www.ddl-island.su'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    RECAPKEY = '6LcFQP8SAAAAAOXJT-Sf2aZpy1ZUgrYiPC8YP1hW'
    RECAPURL = 'http://protect.ddl-island.su/'

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/recherche.php?categorie=99&rechercher=Search&fastr_type=ddl&find={}'.format(
            self.BASE_URL, search_term.encode('ascii', 'ignore').decode('ascii')
        )

    def _fetch_no_results_text(self):
        return u'Affichage des résultat 1 à 0'

    def _fetch_next_button(self, soup):
        next_button = soup.select('table.page td[width="20"] a')
        if next_button:
            return '{}{}'.format(self.BASE_URL, next_button[-1].href)
        # If there are only 2 pages, it shows 1, 2 and thats it...
        page_tds = soup.select('table.page td a')
        if len(page_tds) == 1 and page_tds[0].text == '2':
            return '{}{}'.format(self.BASE_URL, page_tds[0].href)
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.fiche_listing'):
            # TODO - these .html files link off to
            # http://www.stream-island.su/ too
            link = result.select_one('a')
            url = link.href
            if url.endswith('.html'):
                url = url[:-5]
            self.submit_search_result(
                link_url=url,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    @cacheable()
    def _extract_link(self, url):
        self.load_session_cookies()
        soup = self.get_soup(url)
        if soup.select('div.g-recaptcha'):
            # we need to solve a recap.
            soup = self.post_soup(
                url,
                data = {
                    'g-recaptcha-response': self.get_recaptcha_token(),
                    'submit': 'Valider',
                }
            )
            self.save_session_cookies()
        # otherwise, dig out the actual url.
        link = soup.select_one('div.notice table.addlink a')
        return link and link.href or None


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('table.ddls a'):
            url = link.href
            if url.startswith('http://protect.ddl-island.su/'):
                url = self._extract_link(url)
                if 'http' in url:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

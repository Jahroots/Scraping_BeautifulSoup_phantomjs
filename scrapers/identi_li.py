# coding=utf-8

from sandcrawler.scraper import ScraperBase
import json

class IdentiLi(ScraperBase):
    BASE_URL = 'http://www.identi.li'
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, 520], **kwargs)

    def do_search(self, search_term, page=1):
        return self.post(
            self.BASE_URL + '/ajax/acciones_buscador.php',
            data={
                'act': 'posts',
                'ord': 0,
                'cat': 0,
                'tcat': 0,
                'sort': 'ASC',
                'pag': page,
                'search': search_term,
                'mode': 1,
                'rango': 0,
                'id_comu': 0
            }
        ).text.strip()

    def search(self, search_term, media_type, **extra):
        page = 1
        search_result = self.do_search(search_term, page=page)
        search_result = json.loads(search_result)


        if 'text' in search_result and \
                        search_result['text'].find(
                            u'No se encontraron resultados') >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(search_result)

        while self.can_fetch_next():
            page += 1
            search_result = self.do_search(search_term, page=page)
            search_result = json.loads(search_result)
            # Bail out if we have text - it's a flag of no results.
            if 'text' in search_result:
                break
            self._parse_search_result_page(search_result)

    def _parse_search_result_page(self, search_result):
        for result in search_result['data'].values():
            href = self.BASE_URL + '/index.php?topic=' + result['link']
            # Make a soup so we can strip any tags out - they seem to drop
            # spans in with reckless abandon
            title = self.make_soup(result['subject']).text
            season, episode = self.util.extract_season_episode(title)
            self.submit_search_result(
                link_url=href,
                link_title=title,
                series_season=season,
                series_episode=episode,
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        # Just submit jdownloader - the helper will help with that.
        for jdownloader in soup.findAll('input', {'src': 'jdownloader'}):
            if jdownloader.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=jdownloader['href'],
                                         link_title=soup.title.text.replace(' - Identi', '')
                                         )
            # TODO decrypt links
            # Adlure appears to have links, but they appear to be spammy

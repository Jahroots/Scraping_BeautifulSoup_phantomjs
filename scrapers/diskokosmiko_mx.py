# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DiskokosmikoMx(SimpleScraperBase):
    BASE_URL = 'http://diskokosmiko.mx'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def do_search(self, search_term, page=1):
        return self.post_soup(
            self.BASE_URL + '/action/SearchFiles',
            data={
                'Mode': 'List', 'Type': '', 'Phrase': search_term, 'SizeFrom': 0, 'SizeTo': 0, 'Extension': '',
                'ref': 'pager', 'pageNumber': page
            }
        )

    def search(self, search_term, media_type, **extra):
        page = 1
        search_result = self.do_search(search_term, page=page)
        if search_result.find(text=u'No se encontraron resultados') >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(search_result)
        while self.can_fetch_next():
            page += 1
            search_result = self.do_search(search_term, page=page)
            if search_result.find(
                    u'No se encontraron resultados') >= 0:
                break
            self._parse_search_result_page(search_result)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.list_container div.name a')
        if not results:
            self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL+result['href'],
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.find_all('div', 'top_avatar')[-1].text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        try:
            link = soup.select_one('div.file_container')['data-player-file']
        except KeyError:
            link = self.BASE_URL+soup.select_one('form.download_form')['action']
        self.submit_parse_result(
            index_page_title=index_page_title,
            link_url=link,
            link_text=title,
            series_season=season,
            series_episode=episode,
        )

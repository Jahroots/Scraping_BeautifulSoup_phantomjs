# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AmoFilmes(SimpleScraperBase):
    BASE_URL = "http://amofilmes.net"
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'rock'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError('Website no longer required')

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        next_page = soup.find('a', text='Próxima »')
        if next_page:
            return next_page['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('.post-title a'):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.href)

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('.name.post-title.entry-title').text
        season, episode = self.util.extract_season_episode(title)

        for lnk in soup.select('.sexybutton.sexysimple.sexygreen.sexymedium'):
            url = lnk.href
            if ':ptth' in url:
                url = url[37:][::-1]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode)

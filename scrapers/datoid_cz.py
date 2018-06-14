# coding=utf-8
import re
from sandcrawler.scraper import SimpleScraperBase, ScraperBase



class DatoidCz(SimpleScraperBase):
    BASE_URL = 'https://datoid.cz'

    def setup(self):

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "cze"
        self.requires_webdriver = True
        self.webdriver_type = 'chrome'

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, *args, **kwargs):
        kwargs['verify'] = False
        return super(DatoidCz, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['verify'] = False
        return super(DatoidCz, self).post(*args, **kwargs)

    def _fetch_no_results_text(self):
        return u'Nebyly nalezeny žádné soubory ani složky'

    def _fetch_next_button(self, soup):
        link = soup.find('a','next ajax')
        if link:
            return self.BASE_URL+link['href']
        return None

    def _login(self):
        self.post(self.BASE_URL, data={'username':'ChuckMMartinez@teleworm.us', 'password':'123321', 'do':'signInForm-submit'})

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/s/{}'.format(self.util.quote(search_term))

    def _parse_search_result_page(self, soup):
        url = soup._url
        wd = self.webdriver()
        wd.get(url)
        soup = self.make_soup(wd.page_source)
        results = soup.select('a.decryptLink')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            title = result.find('span', 'filename').text
            link_url = self.BASE_URL + result['onclick'].split('href = "')[-1].split('";')[0]
            play_thumb = result.find('div', 'thumb play')
            if play_thumb:
                self.submit_search_result(
                    link_url=link_url,
                    link_title=title,
                )

    def _parse_parse_page(self, soup):
        self._login()
        index_page_title = self.util.get_page_title(soup)
        link = self.BASE_URL +soup.find('script', text=re.compile('streaming.setSource')).text.split('"HQ", "')[-1].split('");')[0].replace('\\', '')
        season, episode = self.util.extract_season_episode(index_page_title)
        self.submit_parse_result(index_page_title=index_page_title,
                                 series_season=season,
                                 series_episode=episode,
                                 link_url=link)

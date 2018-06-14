# -*- coding: utf-8 -*-
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import VideoCaptureMixin


class Cda_pl(SimpleScraperBase, VideoCaptureMixin):
    BASE_URL = 'https://www.cda.pl'
    OTHER_URLS = ['http://www.cda.pl']
    USER_AGENT_MOBILE = False
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'pol'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = ('parse', )

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + "/video/show/" + self.util.quote(search_term.encode('utf-8'))
         #return self.BASE_URL + "/info/" + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u"Niestety, nic nie znaleziono"

    def _fetch_next_button(self, soup):
        nxt = soup.select_one('a[class="btnRed sbmNext fiximg"]') or soup.select_one('#vloaded > div > a')
        if nxt:
            self.log.debug('------------------------')
            return self.BASE_URL + nxt['href']

    def _parse_search_result_page(self, soup):
        all_results = [lnk for lnk in soup.select('.link-title-visit') if '/video' in lnk.href]
        if not all_results:
            self.submit_search_no_results()

        for result in all_results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def parse(self, parse_url, **extra):
        page_source = self.get(parse_url)
        soup = self.make_soup(page_source.text)
        title = soup.select_one('#naglowek > span').text.strip()
        season, episode = self.util.extract_season_episode(title)
        srch = re.search('<video src="(.*?)"', str(soup))
        index_page_title=soup.title.text.strip()
        if srch:
            video_url = srch.group(1)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=video_url,
                series_season=season,
                series_episode=episode
            )

        if soup.text:
            link = re.search("""['"]*file['"]*\s*:\s*['"](.*?)['"]""", page_source.text)
            if link:
                link = link.group(1).decode('rot13').replace('\\', '')
                self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link,
                                series_season=season,
                                series_episode=episode
                            )
            # wd = self.webdriver()
            # wd.get(parse_url)
            # time.sleep(3)
            # for element in wd.find_elements_by_tag_name('param'):
            #     if element.get_attribute('name') == 'flashvars':
            #         value = element.get_attribute('value')
            #         video_match = re.search('file=([^\&]*)', value)
            #         if video_match:
            #

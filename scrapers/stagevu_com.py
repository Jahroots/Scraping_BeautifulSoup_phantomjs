# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Stagevu(SimpleScraperBase):
    BASE_URL = 'http://stagevu.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


        raise NotImplementedError('Website not relevant.')
    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/videos/{}'.format(self.BASE_URL, search_term)

    def _fetch_no_results_text(self):
        return 'No videos were found'

    def _fetch_next_button(self, soup):
        next_img = soup.find('img', attrs={'src': 'http://stagevu.com/img/nextpage.png'})
        if next_img and next_img.parent:
            return u'{}/videos/{}'.format(self.BASE_URL, next_img.parent.href)
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a#movie'):
            if 'youtube' in result['href']:
                # two links - one useful, one not.
                # the useful one has a text.
                if result.text:
                    self.submit_parse_result(
                        link_url=result['href'],
                        link_title=result.text,
                        index_page_title=self.util.get_page_title(soup),
                        parse_url=soup._url
                    )
            else:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text
                )

    def _parse_parse_page(self, soup):
        title = (soup.select_one('.p-cont h2') or soup.select_one('#vidbox h1'))
        if title:
            title=title.text.strip()
            season, episode = self.util.extract_season_episode(title)

            for link in soup.select('.webplayer strong a'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileMirrors(SimpleScraperBase):
    BASE_URL = 'http://filemirrors.info'

    LONG_SEARCH_RESULT_KEYWORD = 'mother'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type, start=0):
        self.start = start
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/index.php?q={}&start={}&tmedia=all&type=all&sort=pd&search=Search'.format(search_term,
                                                                                                           start)

    def _fetch_next_button(self, soup):
        current = soup.select_one('span.navi_current')
        if not current:
            return None
        for sibling in current.next_siblings:
            try:
                href = sibling.find('a').href
            except AttributeError:
                pass
            else:
                if href:
                    if href.startswith('.'):
                        return self.BASE_URL + href[1:]
                    return href
        return None

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        any_found = False
        for result in soup.select('td.fileinfo a'):
            if not result.href:
                continue
            # We only want the internal links
            if result.href.startswith('http'):
                continue
            any_found = True
            title = result.text
            series_season, series_episode = self.util.extract_season_episode(title)

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + result.href,
                link_title=title,
                series_season=series_season,
                series_episode=series_episode,
                )
        if not any_found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # Find this link we don't want.
        download_link = soup.find('a', text='Click here to Download')
        # Then find all same-level links
        for link in download_link.parent.select('a'):
            if not link.href.startswith('http'):
                # Only external.
                continue
            if 'download-client.com' in link.href:
                # skip these.
                continue
            if link.text == 'More':
                continue
            self.submit_parse_result(
                link_url=link['href'],
                link_title=link.text,
                index_page_title=soup.title.text,
            )

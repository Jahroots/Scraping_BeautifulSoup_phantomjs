#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import VideoCaptureMixin


class KSetKz(ScraperBase, VideoCaptureMixin):

    BASE_URL = 'http://kset.kz'
    ITEMS_PER_PAGE = 100

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        raise NotImplementedError('Website Not Found')
        #self.requires_webdriver = ('parse', )

    def _get_search_results(self, search_term, offset=0):
        return self.post_soup(
            'http://kset.kz/search/?mode=video&search_string=%s&length=any'
            '&sort=&show_copies=on' % self.util.quote(search_term),
            data={'scroll_last_object': offset, 'scroll_last_offset': offset}
        )

    def search(self, search_term, media_type, **extra):
        first_page = self._get_search_results(search_term)
        if unicode(first_page).find(u'Ничего не было найдено.') >= 0:
            return self.submit_search_no_results()
        # Pares this page.
        self._parse_search_result_page(first_page)
        offset = self.ITEMS_PER_PAGE
        while self.can_fetch_next():
            page = self._get_search_results(search_term, offset=offset)
            # 0 results flags us as done.
            if not self._parse_search_result_page(page):
                break
            offset += self.ITEMS_PER_PAGE

    def _parse_search_result_page(self, soup):
        results = soup.select('div.video_b')
        for result in results:
            link = result.find('a', 'spr_b')
            image = result.find('img')['src']
            # Try and drag out S..E.. from the title - seems pretty common.
            season, episode = self.util.extract_season_episode(link[
                'title'])
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link['title'],
                image=image,
                series_season=season,
                series_episode=episode,
            )
        return len(results)

    def _video_player_classes(self):
        return ()

    def _video_player_ids(self):
        return ('videoPlayer', )

    def _video_autoplay(self):
        return True

    def _packet_matches_playlist(self, packet):
        return False

    def parse(self, parse_url, **extra):
        if 'kset.kz/video/view' in parse_url:
            # FIXME: We are assuming the video is hosted onsite
            return self.submit_parse_result(index_page_title=self.get_soup(parse_url).title.text.strip(), link_url=parse_url)

        #urls = self._capture_video_urls(parse_url)
        #for url in urls:
            #    self.submit_parse_result(index_page_title=soup.title.text.strip(),link_url=url)

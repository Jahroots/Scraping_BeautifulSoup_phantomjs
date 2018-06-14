# coding=utf-8
import time
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class VoxfilmeonlineNet(SimpleScraperBase):
    BASE_URL = 'https://voxfilmeonline.net'
    OTHERS_URLS = 'http://voxfilmeonline.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rom'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Ne pare rau, dar nu exista acest film'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('.movief a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    @cacheable()
    def _get_videos(self, singleid, server):
        videos = []
        video_soup = self.post_soup(
            '{}/wp-admin/admin-ajax.php'.format(self.BASE_URL),
            data={
                'action': 'samara_video_lazyload',
                'singleid': singleid,
                'server': server,
            }
        )
        for iframe in video_soup.select('iframe'):
            videos.append(iframe['src'])
        return videos

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        for movie_link in soup.select('.video-lazyload-handler'):
            for video in self._get_videos(
                movie_link['data-singleid'],
                movie_link['data-server'],
            ):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=video,
                )


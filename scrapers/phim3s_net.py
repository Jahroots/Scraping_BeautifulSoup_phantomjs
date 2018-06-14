# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, VideoCaptureMixin
from sandcrawler.scraper.caching import cacheable

class Phim3s(SimpleScraperBase):
    BASE_URL = 'http://xemhoathinh.net'
    OTHER_URLS = [
        'http://phim3s.net'
    ]

    LONG_SEARCH_RESULT_KEYWORD = '2016'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "vie"

        self.requires_webdriver = True
        self.webdriver_type='phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/hoat-hinh/' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Chưa có dữ liệu'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.list-film div.inner div.info div.name a'):

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + result['href'],
                link_title=result.text
            )

    # @cacheable()
    # def _extract_url(self, link):
    #     # Their mobile browser is a lot simpler :D
    #     wd = self.webdriver()
    #     wd.get(link)
    #     # Clicking the video sets the 'src'
    #     video = wd.find_element_by_tag_name('video')
    #     video.click()
    #     video = wd.find_element_by_tag_name('video')
    #     url = video.get_attribute('src')
    #     return url

    @cacheable()
    def _extract_url(self, link):
        header = {'Referer': link, 'X-Requested-With': 'XMLHttpRequest'}
        id_link = link.split('/')[-2]
        link_soup = self.get_soup('http://xemhoathinh.net/ajax/episode/embed/?episode_id={}'.format(id_link), headers=header)
        google_link = json.loads(link_soup.text)['video_url_hash'].replace('\\', '')
        page_title = json.loads(link_soup.text)['page_title']
        links = self.get(google_link).text.split('"fmt_stream_map","')[-1].split(']')[0]
        urls = set()
        for url in links.split('|'):
            if 'http' in url:
                urls.add(url.split(',')[0].strip('"'))
        return urls, page_title

    def _parse_parse_page(self, soup):
        title = (soup.select_one('.title.fr').text + '-' + soup.select_one('.name2.fr > h3').text).strip()
        season, episode = self.util.extract_season_episode(title)

        # link = self.get(soup._url+'xem-phim/').text.split('    videoUrl = \'')[1].split('\';')[0]
        soup2 = self.get_soup(soup._url + 'xem-phim/')
        index_page_title = self.util.get_page_title(soup2)
        videolinks = soup2.find_all('a', {'data-type': "watch"})
        for link in videolinks:
            urls, link_title= self._extract_url(self.BASE_URL + '/' + link.href)
            for url in urls:
                self.submit_parse_result(
                    link_url=url,
                    index_page_title=index_page_title,
                    link_title=link_title,
                    season=season,
                    episode=episode
                )


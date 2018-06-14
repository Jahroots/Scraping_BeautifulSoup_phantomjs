# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class XemphimonCom(SimpleScraperBase):
    BASE_URL = 'http://vophim.com/'
    OTHER_URLS = ['http://xemphimon.com', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    REQUIRES_WEBDRIVER = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(XemphimonCom, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/tim-kiem/{search_term}.html'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'cần tìm hiện chưa có trên website.'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'Tiếp')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('span.title-1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        result_url = soup.select_one('a[class="btn btn-green btn-rounded"]')

        headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': result_url.href}
        video_soup = self.get_soup('http://xemphimon.com/ajax/loadEpisode.php?epid={}'.format(result_url.href.split('/')[-1].split('.')[0]), headers=headers)
        ids = json.loads(video_soup.text)
        file_url = ''
        try:
            file_url = ids['Url']
        except KeyError:
            pass
        if not file_url:
            self.webdriver().get(result_url.href)
            soup = self.make_soup(self.webdriver().page_source)
            link_url = soup.select_one('video[class="jw-video jw-reset"]')
            if link_url:
                link_url = link_url['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=result_url.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
            self.webdriver().close()
        else:
            sub = ids['UrlSrt']
            img = ids['Images']
            msg = ''
            url_title = ids['Name'].encode('utf-8')
            link = 'http://play.xemphimon.com/proxy/proxy.php?file={}&sub={}&img={}&msg={}&title={}'.format(file_url, sub, img, msg, url_title)
            movie_headers = {'Referer':result_url.href}
            movie_soup = json.loads(self.get_soup(link, headers=movie_headers).text)
            movie_links = movie_soup['levels']
            for movie_link in movie_links:
                movie_link = movie_link['file']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=result_url.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

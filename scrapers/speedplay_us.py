# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import time
import re

class SpeedplayUs( SimpleScraperBase):
    BASE_URL = 'https://speedplay.us'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?op=search&k={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = ''
        try:
            next_link = soup.find('div', 'paging').find('a', text=u'Next →')
        except AttributeError:
            pass
        if next_link:
            return next_link['href']

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.videobox'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2').text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        id_num = None
        try:
            id_num = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'id'})['value']
        except (AttributeError, TypeError):
            pass
        if id_num:
            fname = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'fname'})['value']
            referer = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'referer'})['value']
            hash_str = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'hash'})['value']
            usr_login = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'usr_login'})['value']
            op = soup.find('form', attrs={"method":"POST"}).find('input', attrs={'name': 'op'})['value']
            data = {'op': op, 'usr_login': usr_login, 'id': id_num, 'fname': fname, 'referer': referer,
                    'hash': hash_str,
                    'imhuman': 'Proceed to video'}
            time.sleep(6)
            post_soup = self.post_soup(soup._url, data=data)
            link_data = post_soup.find('a', attrs={'onclick': re.compile('download_video')})['onclick'].split('(')[-1].split(')')[0].split(',')
            link_id = link_data[0].strip("'")
            mode = link_data[1].strip("'")
            hash_text = link_data[2].strip("'")
            download_soup = self.make_soup(self.get('https://speedplay.us/dl?op=download_orig&id={}&mode={}&hash={}'.format(link_id, mode, hash_text)).text)
            download_link = download_soup.select_one('div.contentbox a')['href']
            if download_link and self.BASE_URL not in download_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=download_link,
                    series_season=season,
                    series_episode=episode,
                    link_text=title,
                )
            online_link_id = post_soup.find('div', id="container").find('div', id='sidebar1').find_next('script').text.split('var|')[-1].split('|')[0]
            online_link = 'https://cdn1.speedplay.us/hls/,{},.urlset/master.m3u8'.format(online_link_id)
            if online_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=online_link,
                    series_season=season,
                    series_episode=episode,
                    link_text=title,
                )
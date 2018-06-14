# -*- coding: utf-8 -*-
import json, re
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Ojin_Tv(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://ojin.tv'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_ALL)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 403], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.title h2 a')
        for result in results:
            if result:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text,
                )

    def _parse_parse_page(self, soup):
        title=soup.select_one('h2').text
        noindex_links = soup.select('noindex iframe')
        if soup.text.find('Sorry, video was deleted.') == -1:
            for noindex_link in noindex_links:
                noindex_link = noindex_link['src']
                if 'youtube' in noindex_link:
                    continue
                if 'moonwalk' in noindex_link:
                    header = {'Referer':soup._url}
                    text = self.get(noindex_link, headers=header).text
                    video_token = re.search("""video_token: '(.*?)'""", text).groups(0)[0]
                    content_type = re.search("""content_type: '(.*?)'""", text)
                    if content_type:
                        content_type = content_type.groups(0)[0]
                        mw_key = re.search("mw_key = '(.*?)'""", text).groups(0)[0]
                        mw_pid = str(re.search("""mw_pid: (.*?),""", text).groups(0)[0])
                        p_domain_id = str(re.search("""p_domain_id: (.*?),""", text).groups(0)[0])
                        ad_attr = '0'
                        data = {'video_token': video_token, 'content_type': content_type, 'mw_key': mw_key,
                                'mw_pid': mw_pid,
                                'p_domain_id': p_domain_id, 'ad_attr': ad_attr,
                                }
                        soup_text = self.make_soup(text)
                        script_text = soup_text.find_all('script', text=re.compile("window\[\'"))[-1].text
                        raw_mw_value = re.search("""= \'(.*)\';""", script_text).groups()[0]
                        mw_value = ''.join(map(lambda x: x.strip().replace("'", ''), raw_mw_value.split('+')))
                        raw_key = re.search("""\]\[(.*)\] =""", script_text).groups()[0]
                        key = ''.join(map(lambda x: x.strip().replace("'", ''), raw_key.split('+')))
                        data[key] = mw_value
                        x_access = re.search("""X-Access-Level\': \'(.*?)\'""", text).groups()[0]
                        headers = {'X-Access-Level': x_access, 'X-Requested-With': 'XMLHttpRequest'}
                        link_soup = json.loads(self.post_soup('http://moonwalk.cc/sessions/new_session', data=data, headers=headers).text)
                        error_code = link_soup['error_code']
                        if not error_code:
                            movie_link = link_soup['mans']['manifest_m3u8']
                            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                     link_url=movie_link,
                                                     link_title=title
                                                     )
                    else:
                        movie_link = noindex_link
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=movie_link,
                                                 link_title=title
                                                 )

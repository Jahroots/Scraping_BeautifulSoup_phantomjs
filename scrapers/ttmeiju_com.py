# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class TtmeijuCom(SimpleScraperBase):
    BASE_URL = 'http://www.ttmeiju.vip'
    OTHER_URLS = ['http://ttmeiju.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/index.php/search/index/keyword/{search_term}/range/0/p/1.html'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return self.BASE_URL+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('table.latesttable td[align="left"]')[1:]:
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
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.hd')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('tbody#seedlist img[ectype="clicknode"]'):
            name = link['name']
            nodetype = link['nodetype']
            if 'otherurl' in nodetype or 'bdurl' in nodetype:
                headers = {'Referer': soup._url}
                data = {'seedid':name, 'nodetype':nodetype}
                other_soup = self.post_soup(self.BASE_URL + '/index.php/seed/nodeclick.html', data=data, headers=headers)
                link = other_soup.select_one('p').text
                if 'magnet' not in link:
                    link = link.replace('..', self.BASE_URL)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
        link = soup.select_one('a[name="miurl"]')
        if link and link.href and 'magnet' not in link['href']:
            text = link.text
            link = link.href.replace('..', self.BASE_URL)

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=text,
                series_season=series_season,
                series_episode=series_episode,
            )

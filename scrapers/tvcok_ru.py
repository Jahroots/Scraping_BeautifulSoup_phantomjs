# -*- coding: utf-8 -*-
import json
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException
from sandcrawler.scraper.caching import cacheable


class TVcok(SimpleScraperBase):
    BASE_URL = 'http://www.tvcok.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + "/search/{}/1.html".format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        if not soup.select('.paginator li'):
            return
        curr = [el for el in soup.select('.paginator li') if not el.find('a')][0]
        nxt = curr.find_next_sibling()
        if nxt and nxt.name == 'li':
            self.log.debug('------------------------')
            return '/'.join(soup._url.split('/')[:-1]) + '/' + nxt.a['href']

    def _parse_search_result_page(self, soup):
        all_results = soup.select('.info h2 a')
        if not all_results:
            self.submit_search_no_results()

        for result in all_results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip()
            )

    @cacheable()
    def _extract_result(self, season, id, tt):
        html = json.loads(
            self.get(
                self.BASE_URL + '/get_movie_code/?movie_id={}&tt={}'.format(
                    id.strip("'"), tt.strip("'")),
                headers={'X-Requested-With': 'XMLHttpRequest',
                         'Accept': 'application/json, text/javascript, */*; q=0.01'}).text)[
            'code']
        # print(html)
        url = self.make_soup(html).select_one('iframe')[
            'src']  # html.split('iframe src=')[1].split(' ')[0]
        season, episode = season.split('__')
        return dict(
            link_url=url,
            series_season=season,
            series_episode=episode
        )

    def _parse_parse_page(self, soup, serie_mode=False):
        title = soup.select_one('.icon-1').text.strip()

        found_items = []
        body = unicode(soup)
        ss_index = body.find('var ss = "')
        end_ss_section_index = body.find(u'// Показываем какой-то сезон')
        if ss_index > 0 and end_ss_section_index > 0:
            ss_script = body[ss_index:end_ss_section_index]
            for ss_section in ss_script.split('var ss = "'):
                if not ss_section:
                    # Skip first one.
                    continue
                season = ss_section[:ss_section.find('"')]
                for episode in ss_section.split(');'):
                    if not episode.strip():
                        # Skip last one.
                        continue
                    id = re.search("'id': (\d+)", episode).group(1)
                    tt = re.search("'tt': '(.*?)'", episode).group(1)
                    if id and tt:
                        found_items.append(
                            (season, id, tt)
                        )
        else:
            raise ScraperParseException('Could not find ss section.')

        index_page_title = self.util.get_page_title(soup)

        for season, id, tt in found_items:
            result = self._extract_result(season, id, tt)
            result['index_page_title'] = index_page_title
            result['link_title'] = title
            self.submit_parse_result(**result)

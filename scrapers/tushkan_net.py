# -*- coding: utf-8 -*-
import json
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Tushkan_net(SimpleScraperBase):
    BASE_URL = 'http://tushkan.club'
    OTHER_URLS = ['http://tushkan.net',]
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        kwargs['allowed_errors_codes'] = [403, ]
        return super(Tushkan_net, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q={}&sfSbm=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C&a=45'.format(
            self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'По запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        links = [a for a in soup.select('.swchItem ') if '\xbb' in str(a)]
        self.log.debug('-' * 30)
        return self.BASE_URL + links[0]['href'] if links else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.news_title a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):

        for iframe in soup.select('div.message iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe['src'],
            )

        try:
            # title = soup.select_one('.message').text.split('\n')[1].split(':',1)[1]
            # or
            hh = re.compile('<b>Оригинальное название:</b>.+')
            title = unicode(
                re.findall(hh, str(soup))[0].split('</b>')[1].strip().replace('\n', '').replace('<br/>', ''), 'UTF-8')
        except Exception as e:
            self.log.exception(e)
            try:
                title = soup.titl[:soup.title.find(u'смотреть')]
            except Exception as ee:
                self.log.exception(ee)
                # self.show_in_browser(soup)
                self.log.debug(soup)
                try:
                    title = soup.find('h1').text[:-41]
                except Exception as eee:
                    self.log.exception(eee)
                    return
                    # raise ScraperParseException(str(eee))

        season, episode = self.util.extract_season_episode(title)

        hh = re.compile('http://.+film/.+.flv')
        tttl = (re.findall(hh, str(soup)))
        if tttl:
            link = tttl[0]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )

        else:
            hh = re.compile('http://.+.txt')
            tttl = (re.findall(hh, str(soup)))
            if not tttl:
                return
            link = tttl[0]
            http = self.get_soup(link)
            link = re.findall("pl:(.+), ", str(http))[0].replace("'", '"').replace(', st:"uppodvideo"})', '').replace(
                ', androidplayer:"1"', '')
            if link:
                # print link
                json1 = json.loads(link)
                pl = json1['playlist']
                for it in pl:
                    try:
                        pl0 = it['playlist']
                    except:
                        pl0 = None
                    if pl0:

                        for itt in pl0:
                            season, episode = self.util.extract_season_episode(itt['file'])

                            self.submit_parse_result(
                                                     link_url=itt['file'],
                                                     link_title=title + ' / ' + itt['comment'],
                                                     series_season=season,
                                                     series_episode=episode)
                    else:

                        season, episode = self.util.extract_season_episode(it['file'])

                        self.submit_parse_result(
                                                 link_url=it['file'],
                                                 link_title=title + ' / ' + it['comment'],
                                                 series_season=season,
                                                 series_episode=episode)

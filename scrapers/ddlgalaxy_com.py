# -*- coding: utf-8 -*-
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper.caching import cacheable

class DdlgalaxyCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.ddlgalaxy.com'
    OTHER_URLS = []
    USERNAME = 'Everned'
    PASSWORD = 'eo0aJei6'

    def setup(self):
        raise NotImplementedError('This domain has expired')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ita'


        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _login(self):
        home_soup = self.get_soup(self.BASE_URL)
        if u'Logout' not in unicode(home_soup):
            username = self.USERNAME
            PASSWORD = self.PASSWORD
            self.post(self.BASE_URL,
                                     data={'login':'submit', 'login_name':username, 'login_password':PASSWORD, 'top_password':'',  'image.x':0, 'image.y':0
                                            }
                                     )

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u'La ricerca non ha prodotto risultati'

    def search(self, search_term, media_type, **extra):
        self._login()
        self.media_type = media_type
        first_page = self.load_search_page(search_term)
        self._parse_search_results(first_page)
        for page in first_page.findAll(
                'a',
                onclick=re.compile('^javascript:list_submit\(\d+\)')):
            if not self.can_fetch_next():
                break
            try:
                page_no = int(page.text)
            except ValueError:
                pass
            else:
                self.log.debug('---------- {} ----------'.format(page_no))
                self._parse_search_results(
                    self.load_search_page(search_term, page_no)
                )

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.short-title a'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def parse(self, parse_url, **extra):
        self._login()
        return super(DdlgalaxyCom, self).parse(parse_url, **extra)

    @cacheable()
    def thanks(self, data):
        post_link = 'http://www.ddlgalaxy.com/engine/ajax/thanks.php'
        post_soup = self.post_soup(post_link, data=data)
        return post_soup

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2.short-title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        id_num = soup._url.split('/')[-1].split('-')[0]
        data={'thanks':'thanksForNews', 'news_id':id_num}
        post_soup = self.thanks(data)
        for link in post_soup.select('pre code'):
            if 'Info sul file' in link.text:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.text.strip(),
                link_title=link.text.strip(),
                series_season=series_season,
                series_episode=series_episode,
            )
        for link in self.util.find_urls_in_text(soup.text):
            if self.BASE_URL in link or 'videolan' in link or len(link)==8:
                continue
            if len(re.findall('http', link)) > 1:
                urls = link.split('http')
                for link in urls[1:]:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url='http'+link.strip(),
                        link_title='http'+link.strip(),
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

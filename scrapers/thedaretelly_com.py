# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re
import base64

class ThedaretellyCom(SimpleScraperBase):
    BASE_URL = 'http://www.mydarewatch.com'
    OTHER_URLS = ['http://www.darewatch.com', 'http://www.thedarewatch.com', 'http://www.thedaretelly.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True


    def _fetch_no_results_text(self):
        return u'We are sorry'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            self.BASE_URL + '/search',
            data={
                'menu': 'search',
                'query': search_term,
            }
        )
        if self._fetch_no_results_text() in unicode(soup):
            return self.submit_search_no_results()

        for result in soup.select('ul.ch-grid div.ch-item'):
            link = result.select_one('a.go_link')
            if link and link.has_attr('href'):
                if '/watch/' in link.href:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
                else:
                    # It's tv - follow the link and suck out episode links.
                    tv_soup = self.get_soup(link.href)
                    image = self.util.find_image_src_or_none(result, 'img')
                    for link in tv_soup.select('div.ch-item a.link'):
                        season, episode = self.util.extract_season_episode(link.text)
                        self.submit_search_result(
                            link_url=link.href,
                            link_title=link.text,
                            image=image,
                            series_season=season,
                            series_episode=episode,
                        )
    def parse(self, parse_url, **extra):
        contents = self.get(parse_url).content
        # Find the 'embeds' and decode each of them.
        for embed in re.findall("embeds\[\d+\]\s*=\s*'(.*?)';", contents):
            body = base64.b64decode(embed)
            link = None
            if body.startswith('http'):
                link = body
            else:
                body_soup = self.make_soup(body)
                iframe = body_soup.select_one('iframe')
                if iframe:
                    link = iframe['src']
            if not link:
                self.log.error('Could not find link in %s', body)
                continue
            self.submit_parse_result(
                link_url=link
            )


    def get(self, url, **kwargs):
        return super(ThedaretellyCom, self).get(
            url, **kwargs)

    def post(self, url, **kwargs):
        return super(ThedaretellyCom, self).post(
            url, **kwargs)
        
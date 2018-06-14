# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ComotinTv(SimpleScraperBase):
    BASE_URL = 'http://comotin.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated. Long time with Webserver error.')


    def _fetch_no_results_text(self):
        return u'Sorry Dewamovie cannot find what are you looking for'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('#FilmKare div.FilmResim'):
            link = result.select_one('a')
            soup= self.get_soup(link.href)
            episodes = soup.select('#Movie-video ul.partlar a')

            if episodes:

                for a in episodes:
                    if a.href:
                        self.submit_search_result(
                            link_url=a.href,
                            link_title=a.text,
                            image=self.util.find_image_src_or_none(result, 'img'),
                        )


            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('iframe.lightsoff'):
            src = link['src']
            if src.find('http') == -1:
                src = 'http:' + src

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=title,
                episode = episode,
                season = season
            )

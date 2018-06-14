# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PapystreamingserieCom(SimpleScraperBase):
    BASE_URL = 'http://papystreamingserie.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Website no Longer required.')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u"Aucun résultat, s'il vous plaît essayer de nouveau"

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select(' ul.list_mt li.item'):
            link = result.select_one('a')
            soup = self.get_soup(link.href)

            seasons = soup.select('div.episode-guide ul li a')

            if seasons and len(seasons) > 0:
                for season in seasons:
                    self.submit_search_result(
                        link_url=season.href,
                        link_title=season.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
            else:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('iframe[data-lazy-src]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['data-lazy-src'],
                link_title=title,
                season = season,
                episode = episode
            )

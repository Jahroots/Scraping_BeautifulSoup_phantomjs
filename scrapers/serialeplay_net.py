# coding=utf-8
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SerialeplayNet(SimpleScraperBase):
    BASE_URL = 'http://serialefilme.net'
    OTHER_URLS = ['http://serialeplay.net', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rom'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return None

    def search(self, search_term, media_type, **extra):
        for media_type in self.MEDIA_TYPES:
            if 'tv' in media_type:
                search_soup = self.get_soup(
                    self.BASE_URL+'/seriale/?s={}'.format(self.util.quote(search_term))
                )
            else:
                search_soup = self.get_soup(
                    self.BASE_URL+'/filme-online/?s={}'.format(self.util.quote(search_term))
                )
            self._parse_search_results(search_soup)

    def _parse_search_results(self, soup):
            found = 0
            for link in soup.select('div.movief a'):
                if '/serial/' in link.href and not soup.text.find('Verifica cu atentie daca ai')>0:
                    series_soup = self.get_soup(self.BASE_URL+link.href)
                    for season_link in series_soup.select('div.keremiya_part a'):
                        ep_soup=self.get_soup(self.BASE_URL+season_link['href'])
                        for ep_link in ep_soup.select('div.filmcontent div.movief a'):
                            ep_title = ep_link.text
                            series_season, series_episode = self.util.extract_season_episode(ep_title)
                            self.submit_search_result(
                                link_url=ep_link.href,
                                series_season=series_season,
                                series_episode=series_episode,
                                link_title=ep_title
                            )
                elif '/filme-online/' in link.href:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                    )
                found = 1
            if not found:
                return self.submit_search_no_results()
            next_link = soup.find('a', text=u'Urmatoarea »')
            if next_link and self.can_fetch_next():
                self._parse_search_results(self.get_soup(
                   self.BASE_URL+next_link['href']
                ))

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        title = soup.select_one('div.yazitip').text.strip()
        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(soup._url)
        for iframe_links in soup.select('div#players iframe'):
            iframe_link = self.BASE_URL+'/Seriale/'+iframe_links['src']
            redirect_url = self.get_redirect_location(iframe_link)
            self.submit_parse_result(
                link_url=redirect_url,
                index_page_title=index_page_title,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )

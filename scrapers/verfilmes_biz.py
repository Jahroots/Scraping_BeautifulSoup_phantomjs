# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class VerfilmesBiz(SimpleScraperBase):
    BASE_URL = 'http://www.verfilmes.biz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'»')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.post'):
            link = result.parent['href']
            ep_soup = self.get_soup(link)
            for ep_links in ep_soup.select('a.bs-episodio'):
                ep_link = ep_links['href']
                ep_title = ep_soup.select_one('h1').text
                self.submit_search_result(
                    link_url=ep_link,
                    link_title=ep_title,
                )
            self.submit_search_result(
                link_url=link,
                link_title=result.parent['title'],
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        try:
            title = soup.select_one('h1').text
        except AttributeError:
            title=index_page_title
        players_links = []
        try:
            players_links = soup.find('div', 'opcoes').find_all('a', attrs={'target':'player'})
        except AttributeError:
            pass
        if players_links:
            for link in players_links:
                mov_soup = self.get_soup(link['href'])
                iframe_link = mov_soup.select('iframe')[-1]
                if 'codplayer.php' in iframe_link['src']:
                    iframe_link = mov_soup.select('iframe')[-2]
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link,
                    link_title=title,
                )
        else:
            ep_links = soup.select('div.itens a')
            season, episode = self.util.extract_season_episode(soup._url)
            for ep_link in ep_links:
                mov_soup = self.get_soup(ep_link['href'])
                iframe_link = mov_soup.select('iframe')[-1]['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link,
                    link_title=title,
                    series_season=season,
                    series_episode=episode,
                )


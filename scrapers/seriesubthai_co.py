# coding=utf-8


from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SeriesubthaiCo(SimpleScraperBase):
    BASE_URL = 'http://www.useries.co'
    OTHER_URLS = ['http://seriesubthai.co', ]

    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'tha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def setup(self):
        raise NotImplementedError('Deprecated. Website only show ads.')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        articles = soup.select('article.tt-l a')
        if not articles:
            return self.submit_search_no_results()
        for article in articles:
            result_soup = self.get_soup(article['href'])
            results = result_soup.find('div', attrs={'id': 'loard_comments'}).find_all('a')
            for result in results:
                player_link = result['href']
                if '/player/' in player_link:
                    self.submit_search_result(
                        link_url=player_link,
                        link_title=self.util.get_page_title(result_soup)
                    )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = ''
        try:
            title = soup.find('h1', 'tt-l tt-full sec-h').text.strip()
        except AttributeError:
            pass
        if title:
            season, episode = self.util.extract_season_episode(title)
            id_num = soup._url.strip('/').split('/')[-1]
            source_link ='http://www.useries.co/player/play.php?id={}&width=950&height=550'.format(id_num)
            movie_soup = self.get_soup(source_link)
            movie_link = movie_soup.text.split('"file":"')[-1].split('"}')[0].replace('\\', '')
            if 'jwplayer' in movie_link:
                movie_link = movie_soup.text.split('file: "')[-1].split('",')[0].replace('\\', '')
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    series_season = season,
                    series_episode = episode,
                    link_url=movie_link,
                    )

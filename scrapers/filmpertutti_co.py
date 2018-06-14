# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmPerTuttiCo(SimpleScraperBase):
    BASE_URL = 'http://www.filmpertutti.black'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ita"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return 'Nessun post da mostrare'

    # def _parse_search_results(self, soup):
    def _parse_search_result_page(self, soup):
        results = soup.select('ul.posts a')
        if not results:
            return self.submit_search_no_results()

        for result in results:
            if '/4k/' not in result.href:
                image = result['data-thumbnail']
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.find('div', 'title').text,
                    image=image,
                )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Pagina successiva »')
        return link['href'] if link else None

    def parse(self, parse_url, **extra):
         for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    # def find_season_episode_timessymbol(self, text):
    #     # Matches "XxY" with html times symbol
    #     m = re.search(u'(\d+)×(\d+)', text, re.UNICODE)
    #     if m:
    #         series, episode = m.groups()
    #         return (int(series), int(episode))
    #     return (None, None)

    def _parse_parse_page(self, soup):
        # Only fetch 'p' within the article - that's the entered content.
        series_text = soup.find(text=re.compile('Prima Stagione'))
        title = soup.find('section', id="content").find('h1').text.strip()
        if series_text:
            articles_blocks = soup.find('section', id="content").find('p').find_all_next('p')
            articles = str(articles_blocks).split('\\n')
            for article in articles:
                block = self.make_soup(article)
                if block.find('p') is None:
                    continue
                if '[' in block.find('p').text:
                    series_text = block.find('p').find_next('p').find_next('p').text
                    links = block.find('p').find_next('p').find_next('p').find_all_next('a')
                    series = series_text.split()[0]
                    if '\xa0':
                        series = u'1\xd701'
                    for link in links:
                        series_season, series_episode = series.encode('utf-8').split('×')[0], series.encode('utf-8').split('×')[1]
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link['href'],
                                                 link_title=title,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )

                else:
                    series_text = block.find('p').text
                    links = block.find('p').find_all_next('a')
                    series = series_text.split()[0]
                    for link in links:
                        if 'filmpertutti.click' in link['href']:
                            continue
                        if '/dmca/' in link['href'] or 'Tnanks' in link['href']:
                            break
                        try:
                            series_season, series_episode = series.encode('utf-8').split('\\xd7')[0], \
                                                        series.encode('utf-8').split('\\xd7')[1]
                        except IndexError:
                            series_season, series_episode = series.encode('utf-8').replace('\u0102\\x97', '\\xd7') \
                                                                .split('\\xd7')[0], series.encode('utf-8')\
                                                                .replace('\u0102\\x97', '\\xd7').split('\\xd7')[0]
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link['href'],
                                                 link_title=title,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )
        else:
            links = soup.find('section', id="content").find_all('a')
            for link in links:
                movie_url = link['href']
                if 'imdb.com' in movie_url or 'filmpertutti.click' in movie_url or 'addtoany.com' in \
                    movie_url or 'filmtv.it' in movie_url:
                    continue
                self.submit_parse_result(index_page_title=title,
                                         link_url=movie_url,
                                         )


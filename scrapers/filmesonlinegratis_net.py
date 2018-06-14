#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase

class FilmesOnlineGratisNet(ScraperBase):

    BASE_URL = 'http://www.filmesonlinegratis.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"
        raise NotImplementedError('The website is disabled')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        links = soup.select(
            'article.miniatura h2.titulo a')
        if not links:
            return self.submit_search_no_results()
        for link in links:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text
            )

        next_button = soup.select('a.nextpostslink')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button[0]['href'])
            )

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        # First check if we have a video series - if so dig deeper.

        title = soup.title.text

        series = soup.select('ul.series')
        if series:
            # We should have a bold '1st/2nd/3rd Temporada'
            # followed by <a>Assister - Episodio 01/02/03</a> in the same
            # container
            for season_title_tag in series[0].findAll('b'):
                # a bit ugly - but find('b', text=...) does not filter as you'd
                # imagine if there are sibling elements.
                if not re.search('.*Temporada.*', season_title_tag.text):
                    continue
                # Calculate our season from that text, then find episodes.
                series_season = self.util.find_numeric(season_title_tag.text)
                for episode_link, episode_soup in self.get_soup_for_links(
                        season_title_tag.parent, 'a'):
                    series_episode = self.util.find_numeric(episode_link.text)
                    # now follow each 'itens' link and get the embeds out of
                    # that.
                    for video_link in episode_soup.select('div.itens a'):
                        href = video_link['href']
                        if href.startswith('?'):
                            href = episode_link['href'] + href
                        video_soup = self.get_soup(href)
                        # If we have another 'div.itens' we're just a
                        # facebook like page.
                        if video_soup.select('div.itens'):
                            continue
                        for iframe in video_soup.select('iframe'):
                            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                     link_url=iframe['src'],
                                                     link_title=title + " " + video_link.text,
                                                     series_season=series_season,
                                                     series_episode=series_episode,
                                                     asset_type=ScraperBase.MEDIA_TYPE_TV
                                                     )


        else:
            # Otherwise dig out our embedded videos - it's a movie.
            for iframe in soup.select('ul.videos iframe'):

                src = None
                if 'src' in iframe.attrs:
                    src = iframe['src']
                elif 'data-src' in iframe.attrs:
                    src = iframe['data-src']
                if src:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_title=title,
                                             link_url=src,
                                             asset_type=ScraperBase.MEDIA_TYPE_FILM
                                             )


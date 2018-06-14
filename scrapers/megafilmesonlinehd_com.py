# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class MegaFilmesOnlineHdCom(SimpleScraperBase):
    BASE_URL = 'http://www.megafilmesonlinehd.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        raise NotImplementedError('The website is deprecated')
        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Resultado da busca para adsfsdfda'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('.thumb.relative ')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
            )

    def _parse_parse_page(self, soup):
        # See if we have a season listing
        series_block = soup.find('div', 'p-serie')
        if series_block:
            self._extract_tv(series_block)
        else:
            self._extract_film(soup)

    def _find_season(self, text):
        # Grab the first digit(s).
        match = re.search('^(\d+).*', text)
        if match:
            return match.group(1)
        return None

    def _extract_tv(self, soup):
        for series in soup.select('div.p-temporada'):
            series_season = self._find_season(
                series.find('div', 'p-titulo').text)
            for row in series.select('tr'):
                # first td is the episode.
                series_episode = row.find('td').text
                for link in row.select(row, 'a'):
                    # skip the first, ad iframe.
                    if link['href'].startswith(self.BASE_URL + '/ads') or not link:
                        continue
                    self._extract_video_page(
                        link['href'],
                        index_page_title=self.util.get_page_title(soup),
                        series_season=series_season,
                        series_episode=series_episode,
                        link_title=link.text,
                        asset_type=ScraperBase.MEDIA_TYPE_TV,
                    )

    def _extract_film(self, soup):
        for iframe in soup.select('.player iframe'):
            if 'src' in iframe.attrs:
                link = iframe['src']
            if 'data-src' in iframe.attrs:
                link = iframe['data-src']
            else:
                raise ScraperParseException('Invalid iframe.')
            # skip the first, ad iframe.
            if link.startswith(self.BASE_URL + '/ads') or not link:
                continue

            self._extract_video_page(
                link,
                index_page_title=self.util.get_page_title(soup),
                asset_type=ScraperBase.MEDIA_TYPE_FILM)
        for url_link in soup.select('a.p-episodio'):
            ttl = soup.find('h3','tt-filme').text
            # print url_link.find_previous('td', 'pt-titulo').text
            self._extract_video_page(
                url_link['href'],
                index_page_title=self.util.get_page_title(soup),
                asset_type=ScraperBase.MEDIA_TYPE_FILM,
                link_title = ttl+' '+url_link.find_previous('td', 'pt-titulo').text)

    def _extract_video_page(self, url, **kwargs):

        url = self._get_video_source(url)
        if url:
            self.submit_parse_result(link_url=url,
                                     **kwargs)

    @cacheable()
    def _get_video_source(self, url):
        return self._extract_video_url(url)

    def _extract_video_url(self, url):
        video_page = self.get_soup(url)

        for iframe in video_page.select('iframe'):
            # Includes ad links to a .org domain.
            if not iframe['src'].startswith(
                    'http://www.megafilmesonlinehd.') and iframe['src'].startswith('http'):
                return iframe['src']

        # Look for
        # <video>
        # <source src="https://goo.gl/sxggjz"
        # type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'>
        # </video>
        for source in video_page.select('source'):

            if source['src'].startswith('http'):
                return source['src']

        # Finally check for jwplayer;
        # 'file': 'https://goo.gl/sxggjz'
        for file in re.findall("'file': '(.*?)',", str(video_page)):
            if file.startswith('http'):
                return file
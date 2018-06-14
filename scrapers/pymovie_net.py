import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PyMovieNet(SimpleScraperBase):
    BASE_URL = "http://www.pymovie.co"
    OTHER_URLS = ["http://www.pymovie.com.mx", "http://pymovie.net", "http://www.pymovie.net", ]

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    SINGLE_PAGE_RESULTS = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        # TODO: Site has "documentaries" which are not searched...
        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?fbuscar=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('article a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('article'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url= self.BASE_URL + link['href'].strip().replace(' ', '-'),
                link_title=link['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_series_listing(self, url):
        for soup in self.soup_each([url]):
            season_links = soup.select('div.listatemporadas a')
            for link in season_links:
                url = self.BASE_URL + link['href']
                self._parse_episode_listing(url)

    def _parse_episode_listing(self, url):
        for soup in self.soup_each([url]):
            title = soup.title.text

            m = re.search('Temporada (\d+)', title, flags=re.IGNORECASE)
            if m:
                season = int(m.groups()[0])

            links = soup.select('div.lista a')
            for link in links:
                link_url = self.util.canonicalise(self.BASE_URL, link['href'])

                episode = None
                m = re.search('^(\d+)', link.text)
                if m:
                    episode = int(m.groups()[0])

                self.submit_search_result(link_url=link_url,
                                          link_title=title + " " + link.text,
                                          series_season=season,
                                          series_episode=episode)

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[itemprop="name"]')
        season, episode = None, None
        if title and title.text:
            title = title.text
            series_season, series_episode = self.util.extract_season_episode(title)

        #iframe
        iframes = soup.select('iframe')
        for iframe in iframes:
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=iframe['src'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )

        #download
        links = soup.select('#vervideo ul.enlaces li.enlaces-l a')
        for link in links:
            if 'http' in link.href:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link.href,
                    link_title=link.text,
                    series_season=season,
                    series_episode=episode
                )


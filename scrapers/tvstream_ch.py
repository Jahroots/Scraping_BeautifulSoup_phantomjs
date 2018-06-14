# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class TvStreamCh(SimpleScraperBase):
    BASE_URL = 'http://tvstream.ch'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.long_parse = True

    def _fetch_no_results_text(self):
        return 'No results'

    def _fetch_next_button(self, soup):
        links = soup.select('table.pagination tr td a')
        for link in links:
            if u'›' in link.text:
                return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('li.searchLi ul li a'):
            title = result.text.strip()
            if not title:
                continue

            link_url = self.util.canonicalise(self.BASE_URL, result['href'])
            # Submit this as our search result, so we end up with a single
            # looooong parse, not many, many, many long parses.
            self.submit_search_result(
                link_title=title,
                link_url=link_url,
            )

    def _parse_series_page(self, soup):
        episode_links = soup.select('div.entry ul li a')
        for item in episode_links:
            title = item.text
            url = self.util.canonicalise(self.BASE_URL, item['href'])

            season, episode = (None, None)

            m = re.search('Season (\d+) Episode (\d+)', title, re.IGNORECASE)
            if m:
                season = int(m.groups()[0])
                episode = int(m.groups()[1])
            yield title, url, season, episode

    def _handle_embed_item(self, item, index_page_title, **extra_kwargs):
        decoded = self.util.unquote(item['name'])
        soup = self.make_soup(decoded)
        iframe = soup.select('iframe')
        for frame in iframe:
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=frame['src'],
                                     **extra_kwargs)

    @cacheable()
    def _handle_interstitial(self, link):
        for soup in self.soup_each([link, ]):
            link_url = soup.select('div#main div.singlepage a')
            if link_url:
                return link_url[0]['href']
        return None

    def _parse_parse_page(self, soup):
        for title, url, season, episode in self._parse_series_page(soup):
            extra_kwargs = {
                'link_title': title,
                'parse_url': url,
                'series_season': season,
                'series_episode': episode,
            }
            for soup in self.soup_each([url, ]):
                embedlinks = soup.select('p.hostEmbeds a')
                for item in embedlinks:
                    try:
                        self._handle_embed_item(item, index_page_title=soup.title.text.strip(), **extra_kwargs)
                    except:
                        self.submit_parse_error("Could not parse embed item")

                otherlinks = soup.select('div.otherResults a')
                link_urls = []

                for item in otherlinks:
                    url = item['href']
                    if url.startswith("/Link/"):
                        url = self.util.canonicalise(self.BASE_URL, url)
                        link_urls.append(url)

                for link in link_urls:
                    link_url = self._handle_interstitial(link)
                    if link_url:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link_url
                                                 )
            break

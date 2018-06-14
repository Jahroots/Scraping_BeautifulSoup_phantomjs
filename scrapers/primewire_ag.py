import re
from sandcrawler.scraper.caching import cacheable
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperFetchException



class PrimewireAg(SimpleScraperBase):
    BASE_URL = 'https://www.primewire.ag'
    OTHER_URLS = ['http://www.primewire.ag','http://www.primewire.is', 'http://www.primewire.sg', 'http://www.primewire.org',
                  'http://www.primewire.to', 'http://www.letmewatchthis.lv', 'http://1channel.biz']

    TRELLO_ID = '80obJzG7'

    def setup(self):

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        # TODO: Site also has "Music"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.long_parse = True

    def _fetch_no_results_text(self):
        return "I couldn't find anything like that"

    def _fetch_next_button(self, soup):
        links = soup.select('div.pagination a')
        if links:
            last = links[-1]
            if '>>' in last.text:
                return self.util.canonicalise(self.BASE_URL, last['href'])

    def _fetch_search_url(self, search_term, media_type):
        section = ""

        if media_type == ScraperBase.MEDIA_TYPE_TV:
            section = "2"
        elif media_type == ScraperBase.MEDIA_TYPE_FILM:
            section = "1"

        url = self.BASE_URL + "/index.php?search_section={0}&search_keywords={1}".format(section,
                                                                                         self.util.quote(search_term))
        return url

    def _parse_search_result_page(self, soup):
        items = soup.select('div.index_container div.index_item')
        for item in items:
            link = item.select('a')

            image = None
            image_element = item.select('img')
            if image_element:
                image = image_element[0]['src']
                if image.startswith("//"):
                    image = "http:%s" % image

            title = None
            title_element = item.select('h2')
            if title_element:
                title = title_element[0].text

            if link and title:
                link = link[0]
                url = self.util.canonicalise(self.BASE_URL, link['href'])
                self.submit_search_result(link_url=url, link_title=title, image=image)

    def _parse_tv_page(self, soup):
        self.log.debug(self.parse_url)
        for episode in soup.select('.tv_episode_item a'):
            link = episode['href']
            series_season, series_episode = None, None
            match = re.search('season-(\d+)/episode-(\d+)', link)
            if match:
                series_season = match.group(1)
                series_episode = match.group(2)
            if 'http' not in link:
                link = self.BASE_URL + link
            self.log.debug(link)
            if self.parse_url == link:
                return
            else:
                self.parse_url = link

            self._parse_parse_page(
                self.get_soup(link),
                series_season=series_season,
                series_episode=series_episode
            )

    @cacheable()
    def follow_go_link(self, url):
        return self.get_redirect_location(url)


    def _parse_parse_page(self, soup):
        self.log.warning('Parsing')

        videos = soup.select('span.movie_version_link a')
        for video in videos:
            if 'javascript' in video.href:
                return
            href = self.follow_go_link(self.BASE_URL + video.href)
            if 'afu.php' in href:
                continue
            self.log.debug(href)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                 link_url=href,
                                 link_name=video['title']
                                 )



    def _handle_external_embed(self, url, **kwargs):
        for soup in self.soup_each([url]):
            title = self.util.get_page_title(soup)
            noframes = soup.select('noframes')
            if noframes:
                link = noframes[0].text.strip()
                link = self.BASE_URL + link if link.startswith('/goto.php') else link
                if link.startswith('http'):
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_title=title,
                                             link_url=link,
                                             **kwargs
                                             )
                    return

            frames = soup.select('frame')
            for iframe in frames:
                url = self.BASE_URL + iframe['src'] if iframe['src'].startswith('/goto.php') else iframe['src']
                if url.startswith('http'):
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_title=title,
                                             link_url=url,
                                             **kwargs
                                             )
                    return

            # self.submit_parse_error("Could not parse page... no frames found")



    def parse_goex(self, soup):
        results = soup.select('span.movie_version_link a')
        for result in results:
            goex_link = self.BASE_URL + result['href']
            link = self.follow_go_link(goex_link)
            season, episode =  self.util.extract_season_episode(result.text)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_title=result['title'],
                                     link_url= link,
                                     series_season=season,
                                     series_episode=episode
                                     )


class WatchFreeMoviesCh(PrimewireAg):
    BASE_URL = "http://www.watchfreemovies.ch"
    OTHER_URLS = []

    def get(self, url, **kwargs):
        return super(WatchFreeMoviesCh, self).get(
            url, allowed_errors_codes=[404, 522], **kwargs)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('------------------------')
        return link['href'] if link else None

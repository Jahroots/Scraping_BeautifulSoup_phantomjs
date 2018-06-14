import re

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, ScraperFetchException


class OneChannelMovieCom(SimpleScraperBase):
    BASE_URL =  'http://www.1channelmovie.com'
    OTHERS_URLS = ['http://1channelmovie.com', 'http://www.1channelmovie.com']

    # it seems we can merge this with PrimewireAg scraper

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL,
        )
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_next_button(self, soup):
        link = soup.select_one('div.pagination a[rel="next"]')
        if link:
            return link.href
        else:
            return None

    def _get_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/%s/' % \
                               self.util.quote(search_term)

    def search(self, search_term, media_type, **extra):
        search_url = self._get_search_url(search_term, media_type)
        for soup in self.soup_each([search_url]):
            self._parse_search_page(soup)

    def _parse_search_page(self, soup):
        results = soup.select('div.index_item a')
        
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            # Skip extra, not useful links.
            if re.match('Watch (.*) for FREE', link['title']):
                continue
            self.submit_search_result(
                link_url=link['href'],
                link_title=link['title']
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_page(soup)

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            # Movie pages have the versions linked directly off the main page.
            self._parse_versionlinks(soup)
            # TV you need to go a page deep (ie each episode)
            for link in soup.select('div.tv_episode_item a'):
                try:
                    episode_soup = self.get_soup(link['href'])
                    self._parse_versionlinks(episode_soup)
                except Exception as e:
                    self.log.exception(e)

    def _parse_versionlinks(self, soup):
        for link in soup.select('span.movie_version_link a'):
            # Follow the link to get the 'real' url.
            url = link['href']
            if 'marketing' in url:
                continue
            if not url.startswith('http'):
                url = self.BASE_URL + url
            try:
                followed_link = self.get(url)
            except Exception:
                self.log.warning('Failed to follow link.')
            else:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=followed_link.url,
                                         link_name=link['title']
                                         )


class VodlyTo(OneChannelMovieCom):
    BASE_URL = 'http://vodly.cr'
    OTHER_URLS = ['http://vodly.to', ]
    SINGLE_RESULTS_PAGE = True

    #def setup(self):
    #    raise NotImplementedError('The website is with "Be right back" message on the front page')

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def _get_search_url(self, search_term, media_type):
        return self.BASE_URL + '/movies/filter?genre=&year=&actor={}&director=&submit='.format(search_term)

    def _parse_search_page(self, soup):
        info_box = soup.select_one('h3[class="comment-reply-title"]')
        if info_box and info_box.text.find("No movies were found based on the above search") > -1:
            return self.submit_search_no_results()
        found = 0
        for link in soup.select('div.item-img a'):
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(link, 'img')
                )
                found = 1
        if found == 0:
            self.submit_search_no_results()

    def _follow_link(self, link):
        soup = self.get_soup(link)
        result = soup.select_one('div.video-section a')
        return result and result.href or None

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            title = soup.select_one('h1').text
            for link in soup.select('a.external_link'):
                url = self._follow_link(link.href)

                if url:
                    self.submit_parse_result(
                        link_url=url,
                        link_title=title,
                    )
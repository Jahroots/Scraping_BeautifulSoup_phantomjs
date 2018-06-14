# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class MegaBoxLi(SimpleScraperBase):
    BASE_URL = 'http://megashares.ch'
    OTHER_URLS = ['http://megashares.ch', 'http://megabox.li', ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_search_url(self, search_term, media_type):
        url = self.BASE_URL + '/index.php?&search=' + \
              self.util.quote(search_term) + \
              '&exact=&actor=&director=&year=&advanced_search=true'
        if media_type == ScraperBase.MEDIA_TYPE_FILM:
            url += '&cat=movie'
        elif media_type == ScraperBase.MEDIA_TYPE_TV:
            url += '&cat=tv'
        return url

    def _fetch_no_results_text(self):
        return 'No result found containing'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        if link:
            return self.BASE_URL + link['href']
        return None

    def __extract_tv(self, url):
        for soup in self.soup_each([url, ]):
            for season in soup.select('div.show_season'):
                series_season = season['data-id']
                for episode in season.select('div.tv_episode'):
                    link = episode.find('a')
                    series_episode = None
                    srch = re.search('Episode (\d+)', str(episode))
                    if srch:
                        series_episode = srch.group(1)
                    yield {
                        'link_url': self.BASE_URL + '/' + link['href'],
                        'link_title': link.text.strip(),
                        'series_season': series_season,
                        'series_episode': series_episode
                    }

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.featured-item'):
            for link_search in ('h3 a', 'h2 a'):
                link = result.select(link_search)
                if link:
                    break
            if not link:
                continue
            link = link[0]
            # If the link goes to a tv show, open that and find
            # episodes/seasons.
            image = self.util.find_image_src_or_none(result, 'div.itm-l img')
            if link['href'].startswith('/watch-tv'):
                for details in self.__extract_tv(self.BASE_URL + link['href']):
                    details.update({
                        'image': image,
                        'link_title':
                            ' '.join([link.text, details['link_title']])
                    })
                    self.submit_search_result(**details)
            else:
                # Otherwise, just submit
                self.submit_search_result(
                    link_url=self.BASE_URL + link['href'],
                    link_title=link.text,
                    image=image,
                )

    @cacheable()
    def __extract_video(self, player_link):
        wrapper_soup = self.get_soup(player_link)

        videos = []

        # Grab the iframe
        iframes = wrapper_soup.select('iframe')
        for iframe_soup in self.soup_each(
                [(('http:' + i['src'])
                  if i['src'].startswith('//')
                  else ((self.BASE_URL + '/' + i['src']) if not i['src'].startswith('http') else i['src']))
                 for i in iframes]):
            # This could be a whole raft of options here.
            # Forms 'click here to continue'
            form = iframe_soup.find('form')
            if form and form['action']:
                videos.append(form['action'])
            # Just a link from this image.
            player_image = iframe_soup.find('img',
                                            {'src': 'images/player.jpg'})
            if player_image and player_image.parent:
                try:
                    videos.append(player_image.parent['href'])
                except (KeyError, TypeError):
                    pass
            # A javascript delayed redreict
            srch = re.search("top\.location\.href = '([^']*)'",
                             str(iframe_soup))
            if srch:
                videos.append(srch.group(1))
            # An iframe!
            for iframe in iframe_soup.select('iframe'):
                if not iframe['src'].startswith('/ads/'):
                    videos.append(iframe['src'])
        return videos

    def parse(self, parse_url, **extra):
        for linkset in self._parse_parse_page(parse_url):
            self.submit_parse_result(**linkset)

    #@cacheable()
    def _parse_parse_page(self, parse_url):
        soup = self.get_soup(parse_url)
        # Follow each link down the sidebar
        links = []
        for sourcelink in soup.select('td.col-left div#links a'):
            links = links + self._extract_info(self.BASE_URL + sourcelink['href'])
        return links


    @cacheable()
    def _extract_info(self, url):
        source_soup = self.get_soup(url)
        info = []

        views_col = source_soup.find('div', 'col3')
        if views_col:
            for player_link in source_soup.select('div#video a'):
                link = player_link.href
                if not link.startswith('http'):
                    link = self.BASE_URL + link
                for video in self.__extract_video(link):
                    if video.startswith('http'):
                        info.append({
                            'index_page_title': self.util.get_page_title(source_soup),
                            'link_url': video,
                        })
        return info


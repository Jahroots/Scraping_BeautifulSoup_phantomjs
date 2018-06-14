# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, ScraperParseException, CacheableParseResultsMixin
from sandcrawler.scraper.caching import cacheable


class EkrankaTV(CacheableParseResultsMixin, ScraperBase):
    BASE_URL = 'http://ekranka.tv'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/videosearch?match=' + \
                     self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _season_and_episode(self, txt):
        """
        Look for
        1 сезон 3 серия
        (1 season 3 episode)
        OR
        1 сезон
        (1 season)
        """
        search = re.search(u'(\d+) сезон (\d+) серия', txt)
        if search:
            return search.groups()
        search = re.search(u'(\d+) сезон', txt)
        if search:
            season = search.group(1)
            return (season, None)
        return (None, None)

    def _parse_search_results(self, soup):
        page_title_text = ''
        page_title = soup.select('div#pageBody h1')
        if page_title:
            page_title_text = page_title[0].text
        else:
            self.submit_parse_error("Could not extract page title")

        if unicode(soup).find(
                u'К сожалению, ни одного видео не найдено') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('div#videos div.item'):

            image = result.select('a.image img')[0]['src']
            title_link = result.select('div > b > a')[0]
            title_soup = self.get_soup(self.BASE_URL + title_link['href'])
            series_list = title_soup.select('div.seriesList')
            if series_list:
                for series_info in series_list:
                    season, episode = self._season_and_episode(series_info.text)
                    # Follow the links within - they're onward links.
                    for link in series_info.select('a'):
                        self.submit_search_result(
                            link_url=self.BASE_URL + link['href'],
                            link_title=page_title_text + " " + link.text,
                            series_season=season,
                            series_episode=episode,
                            image=self.BASE_URL + image,
                            asset_type=ScraperBase.MEDIA_TYPE_TV
                        )
            else:
                video_files = title_soup.select('#videofiles')
                if video_files:
                    for vf in video_files:
                        for a in vf.select('a'):
                            # Safeguard; we shouldn't have any javascript links
                            # as they would be within a tv series setup,
                            # but lets be safe.
                            if a['href'].startswith('javascript'):
                                continue
                            self.submit_search_result(
                                link_url=self.BASE_URL + a['href'],
                                link_title=page_title_text + " " + a.text,
                                image=self.BASE_URL + image,
                                asset_type=ScraperBase.MEDIA_TYPE_FILM
                            )

        next_button = soup.find('a', text=u'следующая →')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    self.BASE_URL + next_button['href'])
            )


    def parse(self, parse_url, **extra):
        if not self.check_for_cached_parse_results(parse_url):
            for result_set in self._parse_parse_page(parse_url):
                self.submit_parse_result(**result_set)

    def _follow_iframes(self, url, depth=1):
        if depth > 5:
            raise ScraperParseException("Reached recursion depth of 5 following"
                "iframe %s" % url)
        # Follow that and look for
        # <iframe src="..."
        iframe_source = self.get(url)

        matches = []
        mtch = re.search('iframe (id="ifr_view" )?src="(.*?)"', iframe_source.text)
        if mtch:
            matches.append(mtch.group(2))

        mtch = re.search('iframe src=\&quot;(.*?)\&quot;', iframe_source.text)
        if mtch:
            matches.append(mtch.group(1))

        for url in matches:
            if url.startswith('http'):
                return url
            else:
                return self._follow_iframes('http://api.ekranka.tv/' + url,
                                            depth=depth+1)
        else:
            raise ScraperParseException("No iframe found on api")


    @cacheable()
    def _parse_parse_page(self, parse_url):
        soup = self.get_soup(parse_url)
        results = []
        index_page_title=soup.title.text.strip()
        for iframe in soup.select('iframe'):
            # Some have an internal link to an api; to add ads?
            if iframe['src'].startswith('http://api.ekranka.tv'):
                url = self._follow_iframes(iframe['src'])
                if url:
                    results.append({
                        'index_page_title': index_page_title,
                        'link_url': url
                    })

            else:
                results.append({
                    'index_page_title': index_page_title,
                    'link_url': iframe['src'],
                })

        for param in soup.findAll('param', {'name': 'movie'}):
            results.append({
                 'index_page_title': index_page_title,
                 'link_url': param['value'],
            })

        # Fall back to these if we don't have anything else.
        # Check for these
        # document.write('<iframe id="ifr_view" src="ifr_player.php?mid=213030&type=html5&r=ekranka" scrolling="no" frameborder="0" width="100%" height="100%" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"></iframe>');
        for result in re.findall('src="(ifr_player.php?.*?)"', unicode(soup)):
            # Just grab the html version
            if 'type=html' in result:
                contents = self.get('http://api.ekranka.tv/' + result).text
                for file in re.findall("file: '.*?'", contents):
                    # Ansd look for
                    # file: '//ufs1.china-cdn88nmbwacdnln8hq8qwe.com/view/JbRAxR5jVchwunArOK6HOg/1481100232/213030.mp4/index-v1-a1.m3u8',
                    results.append({
                        'index_page_title': index_page_title,
                        'link_url': file
                    })


        return results


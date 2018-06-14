# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperFetchException, ScraperException
from sandcrawler.scraper import SimpleScraperBase


class ManiaStreamingCom(SimpleScraperBase):
    BASE_URL = 'http://www.maniastreaming.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        raise NotImplementedError

    def get_soup(self, url, **kwargs):
        # Yuuuuuck
        # Override here to chip in and set our headers to not accept
        # gzip - their server is broken and throws us not-really gzipped
        # data
        kwargs['headers'] = {'Accept-encoding': 'none'}
        result = self.get(url, **kwargs)
        return self.make_soup(result.content)

    def search(self, search_term, media_type, **extra):
        ct = ''
        searchcall = None

        if (media_type == ScraperBase.MEDIA_TYPE_TV):
            ct, searchcall = 'serie', self._parse_tv_search_result_page
        elif (media_type == ScraperBase.MEDIA_TYPE_FILM):
            ct, searchcall = 'movie', self._parse_film_search_result_page
        else:
            raise ScraperException("Media type not supported", media_type=media_type)

        self._do_search(search_term, ct, searchcall)

    def _do_search(self, search_term, ct, searchcall):
        # CT should be 'movie' or 'serie'
        # searchcall should be _parse_tv_search_results or
        #  _parse_movie_search_results
        # Could probably use true/false, but keep it extendable.
        soup = self.get_soup(
            self.BASE_URL +
            '/contents?ct=' + ct +
            '&genre=0&year=0&country=0&search=' +
            self.util.quote(search_term)
        )

        no_results_text = self._fetch_no_results_text()
        if no_results_text and \
                        unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        searchcall(soup)

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            searchcall(
                self.get_soup(
                    next_button_link
                )
            )

    def _fetch_no_results_text(self):
        return u'Désolé, aucun résultat trouvé.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', attrs={'title': 'Next'})
        if link:
            return self.BASE_URL + '/' + link['href']
        return None

    def _find_season_episode(self, text):
        match = re.search('[s|S]aison (\d+) [e|E]pisode (\d+)', text)
        if match:
            return match.groups()
        return (None, None)

    def _parse_parse_page(self, soup):
        # Simple in comparison!
        # Find all a.list-group-item s and submit :)
        for link in soup.select('a.list-group-item'):
            season, episode = self._find_season_episode(
                link['title'])
            redirect_url = self.BASE_URL + '/' + link['href']
            try:
                # Yucky encoding thing - see note above.
                response = self.get(redirect_url,
                                    headers={'Accept-encoding': 'none'})
            except ScraperFetchException, e:
                self.log.warning('Failed to fetch %s: %s',
                                 redirect_url, e)
                continue
            if response.url.startswith(self.BASE_URL):
                # Grab iframes on the page.
                page_soup = self.make_soup(response.content)
                for iframe in page_soup.select('div.plyer iframe'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=iframe['src'],
                                             link_title=link['title'],
                                             series_season=season,
                                             series_episode=episode,
                                             )

                for lnk in page_soup.select_one('a.plyer'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=lnk,
                                             link_title=link['title'],
                                             series_season=season,
                                             series_episode=episode,
                                             )


            else:
                # Otherwise it's taken us to the end url
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=response.url,
                                         link_title=link['title'],
                                         series_season=season,
                                         series_episode=episode,
                                         )

    def _parse_tv_search_result_page(self, soup):
        for link, show_soup in self.get_soup_for_links(
                soup, 'a.pstr', domain=self.BASE_URL + '/'):

            for season_block in show_soup.select(
                    'div.panel-group div.panel'):
                series_season = self.util.find_numeric(
                    season_block.find('h4', 'panel-title').text
                )
                for episode in season_block.select('a.trn'):
                    series_episode = self.util.find_numeric(
                        episode.text)
                    self.submit_search_result(
                        link_url=self.BASE_URL + '/' + episode['href'],
                        link_title=episode['title'],
                        series_season=series_season,
                        series_episode=series_episode,
                        asset_type=ScraperBase.MEDIA_TYPE_TV
                    )

    def _parse_film_search_result_page(self, soup):
        for result in soup.select('a.pstr'):
            image = result.find('img')
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + result['href'],
                link_title=result.find('h3', 'trn').text,
                image=image['src'],
                asset_type=ScraperBase.MEDIA_TYPE_FILM
            )

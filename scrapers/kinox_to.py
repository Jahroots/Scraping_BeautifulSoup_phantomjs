# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class KinoxTo(SimpleScraperBase):
    BASE_URL = 'https://kinox.to'
    OTHERS_URLS = ['http://kinox.to']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "deu"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/Search.html?q=' + \
               self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Keine Einträge vorhanden.'

    def _fetch_next_button(self, soup):
        link = soup.select('a#RsltTableStatic_next')
        if link:
            return link[0]['href']
        return None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('td.Title a'):
            found = True
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text
            )
        if not found:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):

        # If we have a season dropdown, we need to suck out the
        # rel from the select, and add it to the URL
        # http://kinox.to/aGET/MirrorByEpisode/
        # EG: ?Addr=How_I_Met_Your_Mother&SeriesID=2377
        # along with the option value, and each episode that is listed in
        #  the rel of each option.
        # EG:
        # <option value="1" rel="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22" selected="">Staffel 1</option>
        # http://kinox.to/aGET/MirrorByEpisode/?Addr=How_I_Met_Your_Mother&SeriesID=2377&Season=1&Episode=1
        soup = self.get_soup(parse_url)

        season_selector = soup.find('select',
                                    attrs={'id': 'SeasonSelection'})
        if season_selector:
            for option in season_selector.select('option'):
                for episode in option['rel'].split(','):
                    episode_url = self.BASE_URL + \
                                  '/aGET/MirrorByEpisode/' + \
                                  season_selector['rel'] + \
                                  '&Season=' + option['value'] + \
                                  '&Episode=' + episode
                    self._parse_parse_page(
                        self.get_soup(episode_url),
                        {'series_season': option['value'],
                         'series_episode': episode,
                         'asset_type': ScraperBase.MEDIA_TYPE_TV
                         }
                    )
        else:
            self._parse_parse_page(soup, {})

    def _parse_parse_page(self, soup, kwargs):

        # This ones fiddly.
        # There are a bunch of li's with different hosts linked via the
        # rel attribute.
        # EG <li rel="Demolition_Man&Hoster=31">
        # Append that to
        # http://kinox.to/aGET/Mirror/
        # And we get a JSON response with 'Stream'; that's HTML with
        # our link embedded
        for li in soup.select('ul#HosterList li'):
            rel_link = self.BASE_URL + '/aGET/Mirror/' + li['rel']
            stream_json = self.get(rel_link).json()
            embed_soup = self.make_soup(stream_json['Stream'])
            # Grab any iframes
            for iframe in embed_soup.select('iframe'):
                kwargs['link_url'] = iframe['src']
                if 'http' not in kwargs['link_url']:
                    kwargs['link_url'] = self.BASE_URL+kwargs['link_url']
                kwargs['link_title'] = stream_json['HosterName']
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    **kwargs
                )
            # Then any a's or maps
            for link in embed_soup.findAll(['a', 'map', 'area']):
                if 'href' in link.attrs and link['href']:
                    kwargs['link_url'] = link['href'][8:] if link.href.startswith('/Out/?s=') else link.href
                    kwargs['link_title'] = stream_json['HosterName']
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        **kwargs
                    )

# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class DownloadMovieFreeMe(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://dmf.re'
    OTHERS_URLS = ['https://www.downloadmoviefree.me']

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    def setup(self):
        raise NotImplementedError('Deprecated, website not available')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Unfortunately, site search yielded no results. Try to change or shorten your request.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.short_content a'):
            if '/xfsearch/' not in result.href and '#' not in result.href:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text.strip(),
                    #image = self.util.find_image_src_or_none(result, 'img')
                )


    def _parse_parse_page(self, soup):
        self.log.debug(soup._url)
        try:
            title = soup.select_one('h1').text.strip()
        except AttributeError:
            title = soup.select_one('h4.media-heading').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('div.tab_box iframe') + soup.select('div#lightsVideo iframe'):
            if link and link.has_attr('src'):
                self.submit_parse_result(
                    index_page_title= self.util.get_page_title(soup),
                    link_url=link['src'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )

        a = soup.select_one('a[class="btn btn-primary btn-block responsive-width"]')
        if a:
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=a.href,
                link_title=title,
                series_season=season,
                series_episode=episode
            )

    def get(self, url, **kwargs):
        return super(DownloadMovieFreeMe, self).get(url, allowed_errors_codes=[404, 403], **kwargs)
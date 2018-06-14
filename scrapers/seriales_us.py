# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import FlashVarsMixin
#from linkhelpers import gkplugins


class SerialesUs(FlashVarsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.seriales.us'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        raise NotImplementedError('GKPlugin key not avaialble.')

        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = soup.select('.m_m h1 a')
        if not found:
            raise Exception('Nothing found')
            # raise ScraperException('Nothing found')

        for result in found:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        self.soup2parse = soup
        title = soup.select_one('.clm h1').text.strip()

        # season, episode = self.util.extract_season_episode(title)

        for series_link in soup.select('#lcholder li a'):

            serie_soup = self.get_soup(self.BASE_URL + series_link['href'])

            season, episode = series_link['href'].split('/')[-2].split('x')

            for fr in serie_soup.select('div.container iframe'):
                url = fr.get('src') or fr.get('data-src')
                url = 'http:' + url if url.startswith('//') else url
                if url.find('mdn2015x1.com') >= 0:
                    continue
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )

            # <object id="flashplayer" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
            #         width="568" height="340">
            #     <param name="movie" value="/gk2/player.swf"/>
            #     <param name="wmode" value="opaque"/>
            #     <param name="allowFullScreen" value="true"/>
            #     <param name="allowScriptAccess" value="always"/>
            #     <param name="FlashVars"
            #            value="plugins=backstroke-1,timeslidertooltipplugin-3h,/gk2/plugins/proxy.swf&backcolor=0xCCCCCC&controlbar.idlehide=false&controlbar=over&captions.back=false&captions.fontsize=20&captions.fontweight=bold&proxy.link=sw*9e9e0fac85dadcef2c7e21a02fbf6a0af53aab881fe9578bae85305e743022467ec9c8b6c7539a74f51d7f551cdee4c3a668c10eaa63cc762dc53a9474cc95ef030805b770365c9c3e63ba1d2d0bb670f69e27809a3a37f81a01d2b11812e4130b9a777dc20efa56c16d3f847f7b33222cd43dcdf69163f509733062fbaaa2e4"/>
            #     <embed name="flashplayer" src="/gk2/player.swf"
            #        FlashVars="plugins=backstroke-1,timeslidertooltipplugin-3h,/gk2/plugins/proxy.swf&backcolor=0xCCCCCC&controlbar.idlehide=false&controlbar=over&captions.back=false&captions.fontsize=20&captions.fontweight=bold&proxy.link=sw*9e9e0fac85dadcef2c7e21a02fbf6a0af53aab881fe9578bae85305e743022467ec9c8b6c7539a74f51d7f551cdee4c3a668c10eaa63cc762dc53a9474cc95ef030805b770365c9c3e63ba1d2d0bb670f69e27809a3a37f81a01d2b11812e4130b9a777dc20efa56c16d3f847f7b33222cd43dcdf69163f509733062fbaaa2e4"
            #            type="application/x-shockwave-flash" allowfullscreen="true"
            #            wmode="opaque" allowScriptAccess="always" width="568" height="340"/>
            # </object>

            decryption_key = None  # TODO need to found a site-specific key

            if decryption_key:

                flash = serie_soup.find('object', {'id': 'flashplayer'})
                if flash:
                    to_decode = flash.find('param', dict(name="FlashVars"))['value']

                    url = to_decode[to_decode.find('proxy.link=sw*') + 14:]
                    url = \
                    gkplugins.decrypter(198, 128).decrypt(url, base64.urlsafe_b64decode(decryption_key), 'ECB').split(
                        '\0')[0]
                    # print url

                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

import re

import jsbeautifier

from sandcrawler.scraper import ScraperBase, CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import ScraperFetchException
from sandcrawler.scraper.caching import cacheable
import time

class AllUCDotCom(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin,  ScraperBase):
    BASE_URL = 'http://www.alluc.ee'
    RECAPKEY = '6LdrkhgTAAAAAAEnzuuUacDDblJ45CsNFuOcxhRt'

    ALLOW_FETCH_EXCEPTIONS = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        # raise Exception("Deprecated!")

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.proxy_region = 'nl'  # at least not US!

        self.requires_webdriver = True
        #self.webdriver_type = 'phantomjs'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    @cacheable()
    def _extract_link(self, url):
        self.load_session_cookies()
        soup = self.get_soup(url)
        if soup.select('div.g-recaptcha'):
            # we need to solve a recap.
            soup = self.post_soup(
                self.BASE_URL + '/cdn-cgi/l/chk_captcha',
                data={
                    'g-recaptcha-response': self.get_recaptcha_token()

                }
            )

            self.save_session_cookies()
            # return the download urls already
        return None

    def search(self, search_term, media_type, **extra):

        have_results = False
        for url in (
                        self.BASE_URL + '/download/' + self.util.quote(search_term),
                        self.BASE_URL + '/stream/' + self.util.quote(search_term),
        ):

            try:
                soup = self.get_soup(url)
            except ScraperFetchException:
                pass
            except Exception, e:
                self.log.warning(e)
            else:
                have_results = True
                self._handle_page(soup)

        if not have_results:
            self.submit_search_no_results()

    def _handle_page(self, soup):
        for result in soup.select('div.clickable div.title a'):
            if result.href.startswith('/l/'):
                self.submit_search_result(
                    link_url=self.BASE_URL + result.href,
                    link_title=result.text,
                )


        next_link = soup.find('a', text='Next')
        if next_link and self.can_fetch_next():
            self._handle_page(
                self.get_soup(self.BASE_URL + next_link.href)
            )

    def _handle_embed(self, link):
        embed_soup = self.get_soup(self.BASE_URL + link)
        for link in embed_soup.select('a.play1'):
            self.submit_parse_result(index_page_title=embed_soup.title.text.strip(),
                                     link_url=link.href
                                     )

    def parse(self, page_url, **extra):

        self.webdriver().get(page_url)
        page_soup = self.make_soup(self.webdriver().page_source)

        submitted = set()
        submitted.add(self.BASE_URL)
        iframe = page_soup.select_one('#actualPlayer iframe')
        if iframe and iframe.has_attr('src'):
            submitted.add(iframe['src'])
            if iframe['src'].startswith('/source'):
                self._handle_embed(iframe['src'])
            else:
                self.submit_parse_result(index_page_title=self.util.get_page_title(page_soup),
                                         link_url=iframe['src']
                                         )


        for link in page_soup.select('div.linktitleurl a'):
            url = link.href
            if not url.startswith('http'):
                url = self.get_soup(self.BASE_URL + url)._url


            if url and url not in submitted:
                self.submit_parse_result(index_page_title=self.util.get_page_title(page_soup),
                                         link_url=url,
                                         link_title=link.text
                                         )
            submitted.add(url)

        return

        """submitted = set()

        for url in self.util.find_urls_in_text(
                page_soup.select_one('#rawURLStextbox').text
        ):
            self.submit_parse_result(index_page_title=page_soup.title.text.strip(),
                                     link_url=url)
            submitted.add(url)

        for iframe in page_soup.select('iframe'):
            src = iframe['src']
            if src.startswith('/source'):
                self._handle_embed(src)
            else:
                self.submit_parse_result(index_page_title=page_soup.title.text.strip(),
                                         link_url=src
                                         )

        for link in page_soup.select('div.linktitleurl a'):
            url = link.href
            if 'class' in link.attrs and 'clickable' in link['class']:
                # Handle this...
                # <a class="clickable" rel="nofollow">021111.rar</a>
                # <script> var letitl = '021111.rar'; var muhID = 'a8hy3aqp';</script>
                #
                #    if( typeof muhID != 'undefined' && typeof document.getElementById(muhID) != 'undefined' )
                # {
                # 	if (typeof letitl != 'undefined' && typeof leurl == 'undefined' && document.getElementById(muhID).style.display == 'block')
                # 	{
                # 		document.getElementById(muhID).addEventListener("click",
                # 		function(){
                # 			window.location.href = "/source/v"+"id"+"2.php?o"+"=b&mo"+"vid="+letitl;
                # 		});
                # 	}
                # 	else if (typeof letitl != 'undefined' && typeof leurl != 'undefined' )
                # 	{
                # 		document.getElementById(muhID).addEventListener("click",
                # 		function(){
                # 			window.location.href = leurl.replace(/&amp;/g, '&');
                # 		});
                # 	}
                # }
                script = None
                for elem in link.next_siblings:
                    if elem.name == 'script':
                        script = elem
                        break
                if not script:
                    raise ScraperParseException('Next tag is not script: %s', page_url)
                # we effectively just want to grab ,letitl and add it to the
                # redirect script:
                letitl_search = re.search("var letitl = '(.*?)'", str(script))
                if not letitl_search:
                    raise ScraperParseException('Could not find letitl.')
                letitl = letitl_search.group(1)
                url = '/source/vid2.php?o=b&movid=' + letitl

            if url.startswith('/source/vid2.php'):
                url = self.get_redirect_location(self.BASE_URL + url)

            if url not in submitted and url.startswith('http'):
                self.submit_parse_result(index_page_title=self.util.get_page_title(page_soup),
                                         link_url=url,
                                         link_title=link.text
                                         )
                submitted.add(url)

        # And finally go through the 'decrypt('XXX', 'y')' entries
        # Find the first 'script' tag with 'crypt' in it.
        decrypt_block = None
        for script_block in page_soup.select('script'):
            if 'crypt' in script_block.text:
                decrypt_block = script_block.text
                # Remove the line here:.
                #     if (window.callPhantom || window._phantom) return "http://wiki.alluc.to/API-access?ohHi=There&APIalsoWorksForPronTV=justAsk";
                # lolzor!
                decrypt_block = decrypt_block.replace(
                    'if(window.callPhantom||window._phantom)return"http://wiki.alluc.to/API-access?ohHi=There&APIalsoWorksForPronTV=justAsk";',
                    ''
                )

                break

                self.decrypt_block = decrypt_block
                self.log.warning(decrypt_block)

        for dec in re.findall("decrypt\('.*?', '.*?'\)", str(page_soup)):
            for link in self._decrypt(dec):
                if link not in submitted:
                        self.submit_parse_result(
                                index_page_title=self.util.get_page_title(page_soup),
                                link_url=link,
                        )
                        submitted.add(link)
                        """

    @cacheable()
    def _decrypt(self, decrypt_string):
        this_block = self.decrypt_block + '\nreturn ' + decrypt_string
        beaut = jsbeautifier.beautify(this_block)
        result = self.webdriver().execute_script(beaut)
        links = []
        soup = self.make_soup(result)

        for iframe in soup.select('iframe'):
            links.append(iframe['src'])

        return links

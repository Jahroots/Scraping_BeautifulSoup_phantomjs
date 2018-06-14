# coding=utf-8

from sandcrawler.scraper import ScraperBase, \
    SimpleScraperBase, \
    AntiCaptchaMixin, \
    ScraperParseException

from sandcrawler.scraper.caching import cacheable

class SerienjunkiesOrg(SimpleScraperBase, AntiCaptchaMixin):
    BASE_URL = 'http://serienjunkies.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    RECAPKEY = '6LdmhRQTAAAAAAGfWQLCeCmT6CAVKKxu-TibpZ2h'
    RECAPURL = 'http://download.serienjunkies.org/'

    # Note - this does not use the 'front door' search, as it doesn't work!
    # uses AJAX POST version.
    def search(self, search_term, media_type, **extra):
        response = self.post(
            self.BASE_URL + '/media/ajax/search/search.php',
            data={
                'string': search_term,
            },
            headers={
                'Referer': self.BASE_URL
            }
        )
        if response.content == '':
            return self.submit_search_no_results()


        body = response.json()
        if not body:
            return self.submit_search_no_results()

        for link_id, title in body:
            url = self.BASE_URL + '/?cat={}'.format(link_id)
            link_url = self.get_redirect_location(url)
            self.submit_search_result(
                link_url=link_url,
                link_title=title
            )

    @cacheable()
    def _resolve_url(self, url):
        soup = self.get_soup(url)
        download_id_input = soup.find('input', attrs={'name': 's', 'type': 'HIDDEN'})
        if not download_id_input:
            raise ScraperParseException('Could not find download id.')

        download_id = download_id_input['value']
        token = self.get_recaptcha_token()

        data = {
            'g-recaptcha-response': token,
            'action': 'Download',
            's': download_id,
            'newcap': 'true',
        }

        redirect_soup = self.post_soup(
            url,
            data=data,
        )
        # Just grab the first form.
        download_form = redirect_soup.select_one('form')
        if not download_form:
            raise ScraperParseException('Could not find download form.')
        target = download_form['action']
        return self.get_redirect_location(target)



    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.post a'):
            url = link.href
            if len(url) < 1:
                continue

            if url.startswith(self.BASE_URL):
                continue

            if url.startswith('http://download.serienjunkies.org'):
                # Need to follow it!
                url = self._resolve_url(url)



            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.title,
            )

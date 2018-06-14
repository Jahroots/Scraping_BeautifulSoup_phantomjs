import random

from sandcrawler.scraper import ScraperBase


class AllucComAPI(ScraperBase):
    PARSE_RESULTS_FROM_SEARCH = True

    BASE_URL = 'http://www.alluc.ee'
    OTHER_URLS = ['http://api.alluc.ee']
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    RAW_CREDS = """
           lovid1986:edouXei9Kal:6b2ba29bcfee96611c432c2281deb053
           goned1961:xolahSh9:842b5ff02cd331ef7c8b643018aa8b1e
           slivencel:ua8eiJuiS:f880cf71bca847dfd69ea1852d951f21
           manne1993:eghei2tohb:7ed97484ad780961c221f6325c2039d9
           nouters:aec5giec:4a6273bb94cf5e213247f5c41a8529f0
        """
        # Agets1989:uj1TueY8:9bdcc49ad5db079edfbae6d72d97e7b8
        # knitted:1oW6aazohj:67884ae2a79b518a19cef7b053bca5e9
        # Elicted:ieJ8Ove8lai:25e9f3e79ac647454b35ffec63ef72bf
        # monellead:voh2aejeiQu:7a37d0d5f3d456948c0b614497a60797
        # marban:quae2aoj0U:4da113184b00610acae47539c2e24538
        # pong1956:aeWo0meeboB:cdbeea0814ae1d176fe21cc657883bb9
        # lovid1986:edouXei9Kal:6b2ba29bcfee96611c432c2281deb053
        # sirigh:ucie3re0EiT:911fba732a44154d822cd70852b2df83
        # goned1961:xolahSh9:842b5ff02cd331ef7c8b643018aa8b1e
        # brishemed:Yei5eniep:46050338be6ef9d59d577c8b283569fa
        # slivencel:ua8eiJuiS:f880cf71bca847dfd69ea1852d951f21
        # spid1936:aishah4zo:96ed96fad64c26ff26de8fac1625f94a
        # drue1936:upiek1aizah:064cbf3c1f0afa2a2d524869decb653b
        # poicheir:bei8ahnung:e0c908f2960d75172ee60c76f6fd1f55
        # manne1993:eghei2tohb:7ed97484ad780961c221f6325c2039d9
        # nouters:aec5giec:4a6273bb94cf5e213247f5c41a8529f0
        # wellourgerd:ohtierie0:0a4cc73f58e5421ea2ae8540464e26d8
        # supuldn1933:esei3iu7eu:01481655dfab7bf11248bead61300954
        # theem1947:ueshek6sh:6bfb51a4be3fae9cc015d7c7ff18708c
        # fren1973:bohxi9ei:69fa30ac1639a58f776b0bb9bb5d45cf
        # posinever43:ahzah2ee:47f04119d3258565f4558a5c43ed85b8
    # """

    CREDS = [item.split(":") for item in RAW_CREDS.split()]

    RESULT_COUNT = 100

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          self.BASE_URL)

        self.request_limit = 20  # We only have a limited number of results per API key per day

    def _do_search(self, search_term, count=RESULT_COUNT, offset=0):
        cred = random.choice(self.CREDS)
        user, pswd, apikey = cred

        results = []

        for typ in ('stream', 'download'):
            term = search_term + " #newlinks"  # we care about new links mostly!
            url = self.BASE_URL + "/api/search/{typ}/?apikey={key}&query={term}&count={count}&from={offset}&getmeta=1".format(
                typ=typ, key=apikey, count=count, offset=offset,
                term=self.util.quote(term)
            )

            try:
                resp = self.get(url)
                response = resp.json()
                if 'error' in response:
                    return self.submit_parse_error('Could not retrieve results')
                results.extend(response.get('result', []))
            except Exception as err:
                self.submit_parse_error("Could not fetch results: %s" % str(err))

        return results

    def search(self, search_term, media_type, **extra):
        offset = 0
        count = self.RESULT_COUNT

        any_results = False
        while True:
            results = self._do_search(search_term, count=count, offset=offset)
            if results:
                any_results = True

            for result in results:
                parse_url = result.get('metatags', {}).get('sourceurl', 'http://alluc.com')
                title = "%s %s" % (result.get('sourcetitle', ''), result.get('title', ''))
                title = title.strip()

                for url in result.get('hosterurls', []):
                    self.submit_parse_result(index_page_title=title,
                                             parse_url=parse_url,
                                             link_title=title,
                                             link_url=url.get('url', '')
                                             )

            offset += count
            if not self.can_fetch_next() or not results:
                break

        if not any_results:
            self.submit_search_no_results()

            # No need for parse, we are injecting parse results directly from search! :-)

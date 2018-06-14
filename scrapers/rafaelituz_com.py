from sandcrawler.scraper import ScraperBase


class RafaelituzDotCom(ScraperBase):
    def setup(self):
        raise NotImplementedError('http://rafaelituz.com/ is depricated')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, 'http://rafaelituz.com/')
        self.register_url(ScraperBase.URL_TYPE_LISTING, 'http://rafaelituz.com/')

    def get(self, url, **kwargs):
        return super(RafaelituzDotCom, self).get(url, **kwargs)

    def search(self, search_term, media_type, **extra):
        search_url = "http://rafaelituz.com/?s=" + self.util.quote(search_term)

        for soup in self.soup_each([search_url]):
            self._parse_search_page(soup)

    def _parse_search_page(self, soup):
        # Sometimes a "no results" message is displayed
        no_results_box = soup.select('div.date-outer div.date-posts')
        if no_results_box and no_results_box[0].text.strip() == 'Sin resultados':
            return self.submit_search_no_results()

        results = soup.select('div.box-peli')
        if not results:
            return self.submit_parse_error("Could not find result boxes")

        for item in results:
            link_element = item.select('a')
            if link_element:
                link = link_element[0]
                extra = {}

                title_element = link.select('span')
                if title_element:
                    title = title_element[0].text
                    extra['link_title'] = title

                img_element = link.select('img')
                if img_element:
                    img_url = img_element[0].get('src')
                    extra['image'] = img_url

                title_type = self._extract_type(link)
                if title_type:
                    extra['release_type'] = title_type

                if title and u'\xd7' in title:
                    series, episode = self.util.extract_season_episode(title.replace(u'\xd7', "x"))
                    if series and episode:
                        extra.update(series=series, episode=episode)

                self.submit_search_result(link_url=link.get('href'), **extra)

        # Try and walk to the next page
        next_page_link = soup.select('a.nextpostslink')
        if next_page_link and self.can_fetch_next():
            url = next_page_link[0].get('href')
            for next_page in self.soup_each([url]):
                self._parse_search_page(next_page)

    def _extract_type(self, item):
        type_div = item.select('div')
        if not type_div:
            return None

        type_div = type_div[0]
        type_class = type_div.get('class')

        if not type_class:
            return None

        type_class = type_class[0]

        if type_class == '':
            return None

        type_class = type_class.lower()

        TYPE_CLASSES = (
            'dvdrip', 'webrip', 'brscr', 'dvdscr', 'ts', 'ts-hq', 'cam', 'b720p', 'hdtv', 'b1080p', 'brrip7')

        if type_class in TYPE_CLASSES:
            return type_class
        else:
            self.log.warning("Unexpected release type " + type_class)

        return None

    def parse(self, page_url, **extra):
        for page in self.soup_each([page_url]):
            post = page.select('div.post.hentry')
            if not post:
                continue
            post = post[0]

            index_page_title = page.title.text.strip()
            links = post.select('table a')
            for link in links:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_title=link.text,
                                         link_url=link.get('href'))

            for iframe in post.select('iframe'):
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=iframe.get('src'))

            downloads = page.select('div#descarga a.descargarLink')
            for link in downloads:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_title=link.text,
                                         link_url=link.get('href'))

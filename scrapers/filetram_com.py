from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileTramCom(SimpleScraperBase):

    BASE_URL = 'http://filetram.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('Does not have an onsite search - would be '
            'the same as searching using Google ')
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        if media_type in (ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV):
            return self.util.canonicalise(self.BASE_URL, "/video/3-0/" + self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No results containing all your search terms'

    def _parse_search_result_page(self, soup):
        items = soup.select('div.search-item')

        for item in items:
            title = ''
            info = ''
            source = None

            text = item.text
            lines = text.split("\n")
            lines = [line.strip() for line in lines]
            lines = [line for line in lines if line]

            for line in lines:
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Info:"):
                    info = line.replace("Info:", "").strip()
                elif line.startswith("Source:"):
                    source = line.replace("Source:","").strip()

            if not source:
                source = self.BASE_URL

            if not title and not info:
                self.submit_parse_error("Could not extract title or info")
                continue

            urls = item.select('div.url')
            for url in urls:
                self.submit_parse_result(index_page_title=soup.title.text.strip(), parse_url=source,
                                         link_url=url.text.strip(), link_title=title + " " + info)

    def _fetch_next_button(self, soup):
        link = soup.select('a.nextLink')
        if link:
            return self.util.canonicalise(self.BASE_URL, link[0].get('href'))


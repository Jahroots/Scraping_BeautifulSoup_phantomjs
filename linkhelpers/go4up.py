from scraper import ScraperBase
from sandcrawler.scraper.caching import cacheable

class Go4UpHelper(ScraperBase):
    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://go4up.com')

    def expand(self, url, **extra):
        return self.expand_link(url)

    @cacheable()
    def expand_link(self, url):
        results = []

        for soup in self.soup_each([url]):
            title = soup.title.text
            filename = title.replace("Download ", "")

            item_id = url.replace("http://go4up.com/dl/", "")

            # The site dynamically loads the real links via AJAX,
            # but we can grab it by knowing the URL format
            hosts_page_url = 'http://go4up.com/download/gethosts/%s' % item_id

            for soup_hosts in self.soup_each([hosts_page_url]):
                links = []
                links.extend(soup_hosts.select('div.span8 b a'))

                # Each link is then held in a sub page
                sub_page_urls = []

                for link in links:
                    url = link.get('href')
                    if url.startswith("/"):
                        url = 'http://go4up.com' + url

                    sub_page_urls.append(url)

                for sub_soup in self.soup_each(sub_page_urls):
                    links = sub_soup.select('div#linklist center b a')

                    for link in links:
                        results.append(link.get('href'))

        return results

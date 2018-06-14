# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WatchersCollectionBlogspotDe(SimpleScraperBase):
    # Note - this will redirect to the relevant country (eg blogspot.com.au)
    BASE_URL = 'http://watchers-collection.blogspot.ru/'

    LONG_SEARCH_RESULT_KEYWORD = 'The'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(WatchersCollectionBlogspotDe, self).get(url, allowed_errors_codes=[404], **kwargs)

    def __buildlookup(self):
        post_list_soup = self.get_soup('http://watchers-collection.blogspot.ru')
        post_links = post_list_soup.find('a', id='Blog1_blog-pager-older-link')['href']
        movie_to_url = {}
        while post_links:
            post_title = ''
            try:
                post_title = post_list_soup.find('h3', attrs={'itemprop':'name'}).text.strip()
            except AttributeError:
                pass

            if post_title:
                movie_to_url[post_title] = dict(site_url=post_links)

            post_links = ''
            try:
                post_links = post_list_soup.find('a', id='Blog1_blog-pager-older-link')['href']
            except TypeError:
                pass
            if not post_links or '2011-03' in post_links:
                break
            else:
                post_list_soup = self.get_soup(post_links)

        return movie_to_url

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term):
                self.submit_search_result(
                    link_url=page['site_url'],
                    link_title=term,
                )
                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        series_season = series_episode = None
        title = soup.select_one('h3[itemprop="name"]')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        post_block = soup.find('div', 'post hentry').find('div', 'post-body entry-content').find_all('a',href=True)

        for link in post_block:
            if 'clkimg' not in link['href'] and 'sprintrade' not in link['href'] and 'blogspot' not in link['href'] \
                    and 'etsy' not in link['href'] and 'change.org' not in link['href'] and 'realmomsrealviews.com' \
                    not in link['href'] and 'lionbrand' not in link['href'] and 'sitstay' not in link['href'] and \
                            'engraved-gift' not in link['href'] and 'blogger' not in link['href'] and 'facebook' not in \
                    link['href'] and 'rawscanmanga' not in link['href'] and 'twitter' not in link['href'] and \
                            'scottsliquidgold' not in link['href'] and 'tomoson' not in link['href'] and 'webbizideas' \
                    not in link['href'] and 'revivalabs' not in link['href'] and 'softlips' not in link['href'] and \
                            'garlicgold' not in link['href'] and 'monave' not in link['href'] and 'kinderglo' not in \
                    link['href'] and 'lavera' not in link['href'] and 'freecoconutrecipes' not in link['href'] and \
                            'tropicaltraditions' not in link['href'] and 'householdtraditions' not in link['href'] and \
                            'illuminarecosmetics' not in link['href'] and 'daddyvans' not in link[
                'href'] and 'brytonpick' not \
                    in link['href'] and 'eveorganics' not in link['href'] and 'alimapure' not in link['href'] and \
                            'freeforums' not in link['href'] and 'aromahome' not in link['href'] and \
                            'spoilertv' not in link['href'] and 'birdbathandbeyond' not in link['href'] and \
                            'nutraluxemdonline' not in link['href'] and 'snooziesforyou' not in link['href'] and \
                            'orchidbluecosmetics' not in link['href'] and 'sininlinen' not in link['href'] and \
                            'justnaturalskincare' not in link['href'] and 'nandinagreen' not in link['href'] and \
                            'eonsmoke' not in link['href'] and 'greenfoods' not in link['href'] and 'auricblends' \
                    not in link['href'] and 'hazelaid' not in link['href'] and 'naturessheabutter' not in \
                    link['href'] and 'enjoyingtea' not in link['href'] and 'sodastreamusa' not in link['href'] and \
                            'rugalmomknowsbest' not in link['href'] and 'thebellyburner' not in link[
                'href'] and 'zyliethebear' \
                    not in link['href'] and 'gummylump' not in link['href'] and 'seeryusmama' not in link['href'] \
                    and 'csnstores' not in link['href'] and 'bedroomfurniture' not in link['href'] and \
                            'growingababyreviews' not in link['href'] and 'senseo' not in link['href'] and 'artfire' \
                    not in link['href'] and 'cpsc.gov' not in link['href'] and 'hawaiianshavedice' not in \
                    link['href'] and 'mamamakesmoney' not in link['href'] and 'candidclevercosteffectiv' not in \
                    link['href'] and 'atthefenceonline' not in link['href'] and 'childsafety' not in link['href'] \
                    and 'scoopfree' not in link['href'] and 'allcoffeetables' not in link['href'] and \
                            '3garnets2sapphires' not in link['href'] and 'whatsthatbuzz' not in link[
                'href'] and 'sugarncream' \
                    not in link['href'] and 'libman.com' not in link['href'] and 'mnmspecial' not in link['href'] \
                    and 'simplybeingmommy' not in link['href'] and 'eyebuydirect' not in link['href'] and \
                            'heSausagemaker' not in link['href'] and 'thespinngo' not in link[
                'href'] and 'thebraggingmommy' \
                    not in link['href'] and 'mommyisgreen' not in link['href'] and 'momsbestbet' not in link['href'] \
                    and 'boosandrawrs' not in link['href'] and 'lunchopolis' not in link['href'] and 'fabulouswon' \
                    not in link['href'] and 'rubbermaid' not in link['href'] and 'learnonthegosweepstakes' not in \
                    link['href'] and 'purelydogbeds' not in link['href'] and 'vanillavisa' not in link['href'] and \
                            'allbarstools' not in link['href'] and 'penelopesoasis' not in link['href'] and \
                            'itsmemelbie' not in link['href'] and 'electroniccigarettesinc' not in link['href'] and \
                            'sterlingminerals' not in link['href'] and 'yoursnoozies' not in link['href']:

                    self.submit_parse_result(index_page_title=self.util.get_page_title(self.get_soup(parse_url)),
                                             link_url=link['href'],
                                             link_title=link.text,
                                             series_season=series_season,
                                             series_episode=series_episode
                                             )


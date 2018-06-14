# -*- coding: utf-8 -*-
import os
import re
import urllib2
import urlparse

IMAGE_MATCH = re.compile('.*(\.jpe?g|\.gif|\.png|\.ico)$', re.IGNORECASE)
IMDB_SEARCH = re.compile('imdb\.com')
YOUTUBE_SEARCH = re.compile('\.youtube\.co')
FACEBOOK_SEARCH = re.compile('\.facebook\.[co|net]')
ASSET_MATCH = re.compile('.*(\.js|\.css)$', re.IGNORECASE)

class ScraperUtil(object):
    @staticmethod
    def quote(input_string):
        try:
            return urllib2.quote(input_string)
        except KeyError:
            return urllib2.quote(input_string.encode('utf-8'))

    @staticmethod
    def unquote(input_string):
        return urllib2.unquote(input_string)


    @staticmethod
    def convert(string, encoding):
        assert isinstance(string, basestring)

        # We assume any raw input is encoded as utf-8
        if isinstance(string, str):
            string = string.decode('utf-8')
        elif isinstance(string, unicode):
            pass
        else:
            raise TypeError("Not sure how to handle this object")

        return string.encode(encoding)

    @staticmethod
    def canonicalise(base_url, path_url):
        if path_url.startswith('http://') or path_url.startswith('https://'):
            return path_url
        if path_url.startswith('/'):
            return urlparse.urljoin(base_url, path_url)
        else:
            o = urlparse.urlparse(base_url, allow_fragments=False)
            path = os.path.join(o.path, path_url)
            return "".join((o.scheme, "://", o.netloc, '/', path))

    @staticmethod
    def get_base_url(url):
        parts = urlparse.urlparse(url)
        return "".join((parts.scheme, "://", parts.netloc, "/"))

    @staticmethod
    def get_domain(url):
        parts = urlparse.urlparse(url)
        return parts.netloc

    @staticmethod
    def extract_season_episode(string):
        """
        Attempt to extract season and episode information from a string,
        returns a tuple of (season, episode) or (None, None)
        """
        series, episode = (None, None)

        # The series page url contains "<name>_sX_eY"
        m = re.match('.*[sS](\d+)_?[eE](\d+).*', string)
        if m:
            series, episode = m.groups()
            series = int(series)
            episode = int(episode)

        else:
            # Matches "XxY" OR unicode x (\xd7  / ×)
            m = re.search("(\d+)[x|\xd7](\d+)", string)
            if m:
                series, episode = m.groups()
                series = int(series)
                episode = int(episode)
            else:
                m = re.search("S(\d+)E(\d+)", string)
                if m:
                    series, episode = m.groups()
                    series = int(series)
                    episode = int(episode)

                else:
                    # Broke Girls – Season 4 Episode 22 – And the In and Out
                    f = re.findall('(.+?)season\s(\d+)\sepisode\s(\d+)', string + " ", re.I)
                    if f:
                        _, series, episode = f[0]
                        series = int(series)
                        episode = int(episode)

                    else:
                        # Broke Girls –  saison 5 épisode 16
                        f = re.findall(
                            '(.+?)\ssaison\s(\d+)\s\xe9pisode\s(\d+)\s',
                            string + " ", re.I)
                        if f:
                            _, series, episode = f[0]
                            series = int(series)
                            episode = int(episode)
                        else:
                            # 'Dragon Ball Super: Temporada 1 - Episodio 11 (2015)'  TODO can be optimized
                            f = re.findall('(.+?)\stemporada\s(\d+)(.*)\sepisodio\s(\d+)\s', string + " ", re.I)
                            if f:
                                _, series, __, episode = f[0]
                                series = int(series)
                                episode = int(episode)
                            else:
                                # Broke Girls –  saison 5 episode 16
                                f = re.findall(
                                    '(.+?)\ssaison\s(\d+)\s\episode\s(\d+)\s',
                                    string + " ", re.I)
                                if f:
                                    _, series, episode = f[0]
                                    series = int(series)
                                    episode = int(episode)

        return series, episode

    @staticmethod
    def looks_like_video_size(width, height):
        """
        Very naive method to decide whether something could be "video" sized

        See: https://en.wikipedia.org/wiki/Aspect_ratio_%28image%29#Previous_and_currently_used_aspect_ratios
        """
        try:
            width = float(width)
            height = float(height)
        except TypeError:
            return None

        aspect_ratio = width / height

        # IMPROVE? Check the aspect ratio against common known aspect ratios?
        if width > height and 1.2 <= aspect_ratio <= 2.0:
            return True

        return False

    @staticmethod
    def find_numeric(text):
        """
        For a given string remove all non-numeric text, returning None in
        case of failure/no numerics found.

        Can be used to naively find season/episode info from a block of text.
        """
        text_digits = \
            re.sub('[^\d]', '', text)
        if not text_digits:
            return None
        try:
            return int(text_digits)
        except ValueError:
            return None

    @staticmethod
    def check_for_strings(text, strings):
        """
        Return True False as to whether a list of strings is found in
         the text.  May be quicker to make a big regex...
        """
        for string in strings:
            if text.find(string) >= 0:
                return True
        return False

    @staticmethod
    def get_page_title(soup):
        """
        Returns the page title text or None
        """
        title = soup.select("html head title")
        if title:
            return title[0].text
        return None

    @staticmethod
    def find_urls_in_text(text,
        skip_images=True,
        skip_imdb=True,
        skip_youtube=True,
        skip_assets=True,
        skip_facebook=True,
        max_chars=50000
        ):
        """
        Attempts to dig out http(s) urls from a chunk of text.
        Delimits on whitespace, quote or tag start (<)
        """
        # If provided (by defualt 50K) cut the text before regexing.
        if max_chars:
            text = text[:max_chars]
        for link in re.findall('(https?://[^\s|\<|\"\']*)', text):
            if skip_images and IMAGE_MATCH.match(link):
                continue
            if skip_assets and ASSET_MATCH.match(link):
                continue
            if skip_imdb and IMDB_SEARCH.search(link):
                continue
            if skip_youtube and YOUTUBE_SEARCH.search(link):
                continue
            if skip_facebook and FACEBOOK_SEARCH.search(link):
                continue
            yield link

    @staticmethod
    def find_image_src_or_none(soup, css_selector, prefix=None):
        """
        Finds an image tag based on the css_selector; if found returns the src,
        otherwise, None.
        """
        img = soup.select_one(css_selector)
        if img:
            img_src = img.get('src', img.get('data-original'))
            if prefix:
                return u'{}{}'.format(prefix, img_src)
            return img_src
        return None

    @staticmethod
    def find_file_in_js(text):
        """
        Digs out XXX in a chunk of text for the format:
        "file":"XXXXX"

        yields them as a generator.
        """
        for url in re.findall("""['"]*file['"]*\s*:\s*['"](.*?)['"]""", text):
            yield url

    @staticmethod
    def get_href_or_none(soup, css_selector):
        """
        Finds an link address based on the css_selector; if found returns the href, otherwise, None.
        """
        link = soup.select_one(css_selector)
        return link['href'] if link else None

    @staticmethod
    def search_term_to_search_regex(search_term):
        """
        Builds a regex to flexibly compare a search term.

        Ported from per:
        $term =~ s/&/(?:and|&)/g;
        $term =~ s/[,:.'"-]/.?/g;
        $term =~ s/\s/.{0,7}/g;

        $term =~ s/\b(?:2|two|II)\b/(?:2|two|II)/;
        $term =~ s/\b(?:3|three|III)\b/(?:3|three|III)/;
        $term =~ s/\b(?:4|four|IV)\b/(?:4|four|IV)/;

        $term = "/$term/";
        """

        # & -> & or and
        search_term = re.sub('&', '(?:and|&)', search_term)
        # Ignore punctuation
        search_term = re.sub('[,:.\'"-]', '.?', search_term)
        # Include multiple spaces.
        search_term = re.sub('\s', '.{0,5}', search_term)

        search_term = re.sub(u'(?:2|two|II)', '(?:2|two|II)', search_term)
        search_term = re.sub(u'(?:3|three|III)', '(?:3|three|III)', search_term)
        search_term = re.sub(u'(?:4|four|IIII)', '(?:4|four|IIII)', search_term)

        return re.compile(search_term, re.IGNORECASE)

    @staticmethod
    def extract_meta_refresh(soup):
        """
        Extracts url from

        <meta http-equiv="refresh" content="0; url=http://site.name/path/to/url?query=arg"/>
        :param soup:
        :return:
        """
        meta = soup.select_one('meta')
        if meta:
            url = meta['content'][meta['content'].index('url=') + 4:]
            if url:
                return url
        return None

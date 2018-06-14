from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.exceptions import ScraperParseException

import re
import base64
from Crypto.Cipher import AES

class JDownloaderHelper(ScraperBase):

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            'http://127.0.0.1:9666/flash/addcrypted2')

    def expand(self, url, **extra):
        # We need a jdownloader key and text.
        # Grab that from the kwargs, if available, or from the URL.
        # Note we're not using urlparse - we don't want to escape as it
        # causes issues with the decrypt.
        key = text = None
        if 'jdownloader_key' in extra and extra['jdownloader_key']:
            key = extra['jdownloader_key']
        else:
            search = re.search("""return\+%27(\d+)%27%3B""", url)
            if search:
                key = search.group(1)
        if not key:
            raise ScraperParseException('Key not found.')
        if 'jdownloader_data' in extra and extra['jdownloader_data']:
            text = extra['jdownloader_data']
        else:
            search = re.search('crypted=([^\&]*)', url)
            if search:
                text = search.group(1)
        if not text:
            raise ScraperParseException('Text not found.')
        # This is sometimes returning html snippets - grab the text out
        # XXX not sure if it will ever return <a href="...">
        decoded_soup = self.make_soup(self.decode_jdownloader(key, text))
        return decoded_soup.text.strip()

    def decode_jdownloader(self, key, encrypted):
        key = base64.b16decode(key)
        encrypted = base64.b64decode(encrypted)
        # `key` is used as both the Key and IV
        cypher = AES.new(key=key, mode=AES.MODE_CBC, IV=key)
        plain = cypher.decrypt(encrypted)
        return plain



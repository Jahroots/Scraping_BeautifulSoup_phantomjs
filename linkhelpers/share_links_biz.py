from sandcrawler.scraper import ScraperBase

import time
import base64
import re

import binascii
import base64
from Crypto.Cipher import AES


class ShareLinksBizHelper(ScraperBase):

    TEST_URL = "http://share-links.biz/_bntqclnntyku"

    TEST_RESULTS = [""]

    DOMAIN = 'http://share-links.biz'

    HEADERS = {
        'Host': 'share-links.biz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
            'image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 '
            'Safari/537.36'
    }

    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            self.DOMAIN)

        raise NotImplementedError('Website Not Available')


    @staticmethod
    def __decrypt(rsdf):
        key = binascii.unhexlify('8C35192D964DC3182C6F84F3252239EB4A320D2500000000')
        iv = binascii.unhexlify('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        IV_Cipher = AES.new(key, AES.MODE_ECB)
        iv = IV_Cipher.encrypt(iv)

        aes = AES.new(key, AES.MODE_CFB, iv)

        rsdf = ''.join([c for c in rsdf if c in '0123456789abcdefABCDEF'])
        data = binascii.unhexlify(''.join(rsdf.split())).splitlines()

        urls = []

        for link in data:
            link = base64.b64decode(link)
            link = aes.decrypt(link)
            link = link.replace('CCF: ','')
            urls.append(link)

        return urls


    def expand(self, url, **extra):

        page_soup = self.get_soup(url, headers=self.HEADERS)

        referer_headers = self.HEADERS.copy()
        referer_headers.update({'Referer': url})

        # It throws back junk results if you get the main page, then the
        # images too quickly afterward.
        time.sleep(3)

        # Grab all images on the page.
        for img in page_soup.select('img'):

            # Only use images with correct alt text.
            alt_text = img.get('alt', '')
            if 'dlc container' not in alt_text and \
                'rsdf container' not in alt_text:
                continue

            # Suck out matching onclicks.
            m = re.search("_get\('([A-Za-z0-9=]+)',\s(\d+), '([a-z]+)'",
                img.get('onclick', ''))
            if not m:
                continue

            token, module, key = m.groups()
            if key != 'rsdf':
                continue

            dlc_template = "{0}/get/{1}/{2}".format(self.DOMAIN, key, token)
            time.sleep(1)

            req = self.get(
                dlc_template,
                headers=referer_headers)

            return self.__decrypt(req.content)
        return []

if __name__ == '__main__':
    print ShareLinksBizHelper().expand(ShareLinksBizHelper.TEST_URL)

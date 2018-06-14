import json
import base64
import logging
import zipfile
import os
import selenium
import selenium.webdriver

SANDCRAWLER_ROOT = \
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ADBLOCK_EXTENSION = \
    os.path.join(SANDCRAWLER_ROOT, '3rdparty', 'uBlock.chromium-0.9.4.0.crx')

log = logging.getLogger('browser')

MANIFEST_JSON = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

BACKGROUND_JS = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%(proxy_host)s",
            port: parseInt(%(proxy_port)s)
          },
          bypassList: []
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%(proxy_user)s",
            password: "%(proxy_pass)s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
"""

def _build_chrome_extensions(
        adblock=True,
        proxy_config=None
):
    extensions = []

    if adblock:
        data = open(ADBLOCK_EXTENSION).read()
        encoded = base64.b64encode(data).decode('utf-8')
        log.info("Extension size: %d (encoded: %d)", len(data), len(encoded))
        extensions.append(encoded)

    if proxy_config and proxy_config.get('http'):
        # In order to get Chrome to honour username and password
        # for proxies (AND NOT JUST FAIL SILENTLY, FFS) build a tiny
        # plugin that has permission to set proxy details.
        first_half, second_half = proxy_config['http'].split('@')
        username, password = first_half[len('http://'):].split(':')
        host, port = second_half.split(':')

        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr(
                "manifest.json",
                MANIFEST_JSON
            )
            background_js = BACKGROUND_JS % {
                'proxy_host': host,
                'proxy_port': port,
                'proxy_user': username,
                'proxy_pass': password,
            }
            zp.writestr(
                "background.js",
                background_js
            )

        data = open(pluginfile).read()
        encoded = base64.b64encode(data).decode('utf-8')
        extensions.append(encoded)

        # THIS NO LONGER WORKS WITH AUTHENTICATED PROXIES :(
        # capabilities['proxy'] = {
        #     'proxyType': 'manual',
        # }
        # proxy_str_bits = []
        # if proxy_config.get('http'):
        #     capabilities['proxy']['httpProxy'] = proxy_config['http']
        #     proxy_str_bits.append("http=%s" % (proxy_config['http']))
        # if proxy_config.get('https'):
        #     capabilities['proxy']['sslProxy'] = proxy_config['https']
        #     proxy_str_bits.append("https=%s" % (proxy_config['https']))
        # proxy_str = ';'.join(proxy_str_bits)
        # capabilities['chromeOptions']['args'] = ["proxy-server=%s" % proxy_str]
    return extensions

def create_simple_driver(
        driver_url,
        driver_type=None,
        chromedriver_binary=None,
        adblock=True,
        proxy_config=None,
        page_load_timeout=None,
        implicit_wait=None,
        user_agent=None,
        ):

    # Turn off selenium debug logging.
    seleniumlogger = logging.getLogger(
        'selenium.webdriver.remote.remote_connection')
    seleniumlogger.setLevel(logging.INFO)

    if user_agent is None:
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/43.0.2357.125 Safari/537.36'

    if driver_url == 'phantomjs':
        log.info('Starting phantom browser.')
        capabilities = {
            "phantomjs.page.settings.userAgent": user_agent
        }

        service_args = []
        if proxy_config and proxy_config.get('http'):
            first_half, second_half = proxy_config['http'].split('@')
            username, password = first_half[len('http://'):].split(':')
            host, port = second_half.split(':')


            service_args.append(
                '--proxy={}:{}'.format(host, port)
            )
            service_args.append(
                '--proxy-auth={}:{}'.format(username, password)
            )

        driver = selenium.webdriver.PhantomJS(
            desired_capabilities=capabilities,
            service_args=service_args
        )
    elif driver_url == 'chrome':
        log.info('Starting Chrome driver.')
        capabilities = {
            'loggingPrefs': {
                'driver': 'INFO',
                'browser': 'ALL',
                'server': 'ALL',
                'client': 'ALL',
                'performance': 'ALL',
            },
            'chromeOptions': {
                'perfLoggingPrefs': {
                'enableNetwork': True,
                },
            },
        }

        extensions = _build_chrome_extensions(
            adblock=adblock,
            proxy_config=proxy_config
        )
        if extensions:
            capabilities['chromeOptions']['extensions'] = extensions

        if user_agent:
            capabilities['chromeOptions']['args'] = ['--user-agent=%s' % user_agent]

        driver = selenium.webdriver.Chrome(
            desired_capabilities=capabilities,
        )
    else:
        log.error('Starting Remote.')
        capabilities = {
            'loggingPrefs': {
                'driver': 'INFO',
                'browser': 'ALL',
                'server': 'ALL',
                'client': 'ALL',
                'performance': 'ALL',
            },
            'chromeOptions': {
                'perfLoggingPrefs': {
                'enableNetwork': True,
                },
            },
        }

        extensions = _build_chrome_extensions(
            adblock=adblock,
            proxy_config=proxy_config
        )
        if extensions:
            capabilities['chromeOptions']['extensions'] = extensions

        driver = selenium.webdriver.Remote(
            driver_url,
            desired_capabilities=capabilities,
            keep_alive=True,
        )

    if page_load_timeout:
        driver.set_page_load_timeout(page_load_timeout)

    if implicit_wait:
        driver.implicitly_wait(implicit_wait)

    return driver


def extract_network_logs(driver, message_types=('Network.responseReceived', 'Network.requestWillBeSent')):
    messages = driver.get_log('performance')
    packets = []

    for msg in messages:
        packet = msg['message']
        packet = json.loads(packet)
        packet = packet['message']

        if not message_types or packet.get('method') in message_types:
            packets.append(packet)

    return packets



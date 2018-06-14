import logging
import requests
import json
import time

import selenium.webdriver.common.action_chains
import selenium.common.exceptions

from sandcrawler.scraper.browser import extract_network_logs

logger = logging.getLogger('videocapture')

class VideoCaptureMixin(object):
    
    @property
    def vcm_log(self):
        if hasattr(self, 'log'):
            return self.log
        else:
            return logger

    def _http_get(self, url, **kwargs):
        if hasattr(self, 'get'):
            return self.get(url, **kwargs)
        else:
            return requests.get(url, **kwargs)

    def _video_player_classes(self):
        return ('uppod_style_video', )

    def _video_player_ids(self):
        return ('flashVideo', 'flashplayer', 'flashPlayer', 'player',
            'flvplayer_wrapper')

    def _trigger_in_center(self):
        return True

    def _video_autoplay(self):
        """
        If videos will play without intervention, set this to True in your
        subclass.
        """
        return False

    def _get_video_containers(self, driver):
        containers = []
        for css_class in self._video_player_classes():
            try:
                element = driver.find_element_by_class_name(css_class)
            except Exception as err:
                self.vcm_log.info("couldn't find element by class '%s': %s", css_class, err)
            else:
                if element:
                    containers.append(element)

        for element_id in self._video_player_ids():
            try:
                element = driver.find_element_by_id(element_id)
            except Exception as err:
                self.vcm_log.info("couldn't find element by id '%s': %s", element_id, err)
            else:
                if element:
                    containers.append(element)

        return containers


    def _video_wait_time(self):
        """
        Time to wait for ads and video to load and play
        """
        return 45

    def _is_video_mime_type(self, typ):
        if typ.startswith("video/"):
            return True
        else:
            return False

    def _is_video_url(self, url):
        return url.endswith(('flv', 'mp4'))

    def _minimum_video_size(self):
        return 0 #(1024 * 1024) # 2MB

    def _maximum_playlist_size(self):
        return (1024 * 32) # 32KB

    def _clear_popups(self, driver):
        for handle in driver.window_handles[1:]:
            driver.switch_to_window(handle)
            driver.close()
            time.sleep(5)
        # and back to the main one.
        driver.switch_to_window(driver.window_handles[0])


    def _click_element(self, element, driver, x_offset=0, y_offset=0):
        chain = selenium.webdriver.common.action_chains.ActionChains(driver)
        if self._trigger_in_center() and not x_offset and not y_offset:
            elementsize = element.size
            x_offset = elementsize['width'] / 2
            y_offset = elementsize['height'] / 2

        if x_offset or y_offset:
            chain.move_to_element_with_offset(element, x_offset, y_offset)
        else:
            chain.move_to_element(element)
        chain.click()
        chain.perform()

    def use_embed_element(self):
        return True

    def _trigger_container(self, container, driver, action='play'):
        """
        Trigger video container to play
        """
        self.vcm_log.debug("Triggering...")


        embed = None
        if self.use_embed_element():
            try:
                embed = container.find_element_by_tag_name('embed')
                self._click_element(embed, driver)
            except Exception as err:
                self.vcm_log.warning("Embed click err: %s", err)

        if not embed:
            self._click_element(container, driver)


    def _capture_video_logs(self, page_url, cleanup=True):
        # Try and get browser from ScraperBase if present...
        driver = self.webdriver()

        try:
            driver.get(page_url)
        except selenium.common.exceptions.TimeoutException:
            # Sometimes there are a bunch of tracking tags and junk
            # that just take an age to load, if at all.
            # if we hit one, just keeping going and hopef for the best.
            self.vcm_log.warning(
                'Hit timeout loading %s, attempting to continue',
                page_url
            )
            pass

        containers = self._get_video_containers(driver)

        self.vcm_log.info("Found %d containers", len(containers))
        if not containers:
            return []
        for container in containers:
            self.vcm_log.debug("Found container")
            if not self._video_autoplay():
                self._trigger_container(container, driver)
            self.vcm_log.debug("Sleeping")
            time.sleep(self._video_wait_time())
            self.vcm_log.debug("Wake up")
            self._trigger_container(container, driver, action='stop')


        logs = extract_network_logs(driver)
        self.vcm_log.info("Found %d total logs", len(logs))
        logs = self._filter_network_logs(logs)

        self.vcm_log.info("Found %d filtered logs", len(logs))

        return logs

    def _capture_video_urls(self, page_url, cleanup=True):
        logs = self._capture_video_logs(page_url, cleanup=cleanup)
        urls = []
        for log in logs:
            files = log.get('playlist_files')
            if files:
                urls.extend(files)
            else:
                urls.append(log.get('url'))
        return list(set(urls))

    def _packet_matches_video(self, packet):
        resp = packet['params'].get('response')
        if not resp:
            return False

        matched = False

        mime_type = resp.get('mimeType')
        if mime_type and self._is_video_mime_type(mime_type):
            matched = True

        if self._is_video_url(packet['url']):

            matched = True

        if matched:
            headers = resp.get('headers', {})
            content_len = headers.get('Content-Length', 0)
            content_len = int(content_len)
            if content_len < self._minimum_video_size():
                self.vcm_log.warning('Discarding video of length: %s',
                    content_len)
                matched = False

        return matched

    def _get_playlist(self, packet):
        try:
            resp = packet['params'].get('response')
            url = packet['url']
            headers = {}
            keys = ('Cookie', 'X-Requested-With', 'Host', 'Referer')
            packet_headers = resp.get('requestHeaders', {})
            for key in keys:
                headers[key] = packet_headers.get(key)

            r = self._http_get(url, headers=headers)
            obj = json.loads(r.content)
            playlist = obj.get('playlist', [])
            files = []
            if playlist:
                for item in playlist:
                    file = item.get('file')
                    if file:
                        files.append(file)
            if files:
                packet['playlist_files'] = files
                return True
        except Exception as err:
            self.vcm_log.info("Error getting playlist: %s", err)

    def _packet_matches_playlist(self, packet):
        resp = packet['params'].get('response')

        if not resp:
            return False

        mime_type = resp.get('mimeType', '')
        if not (mime_type.startswith("text/") or 'json' in mime_type or 'javascript' in mime_type):
            return False

        requested_with = resp.get('requestHeaders', {}).get('X-Requested-With', '')
        if not ('Flash' in requested_with or 'Shockwave' in requested_with):
            return False

        return True

    def _filter_network_logs(self, logs):

        filtered = []

        for packet in logs:
            resp = packet['params'].get('response')
            req = packet['params'].get('request')

            matched = False
            url = None

            if resp:
                url = resp.get('url')
            if req:
                url = req.get('url')

            packet['url'] = url

            if self._packet_matches_video(packet):
                packet['type'] = 'video_file'
                matched = True
            elif self._packet_matches_playlist(packet):
                if self._get_playlist(packet):
                    packet['type'] = 'video_playlist'
                    matched = True

            if matched:
                self.vcm_log.info("Matched URL: %s", url)
                filtered.append(packet)

        return filtered

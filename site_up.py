#!/usr/bin/python

import sys
import time
import urllib2
import urlparse
import platform

import alerts


INTERVAL = 10  # seconds
TIMEOUT = 30  # seconds
THRESHOLD = 3  # recent failures


def monitor_site(url):
    tag = urlparse.urlparse(url).hostname
    local_name = platform.node()

    recent_failures = 0
    while True:
        try:
            request = urllib2.Request(url)
            request.add_header("User-Agent", "site-up monitor by /u/spladug")
            urllib2.urlopen(request, timeout=TIMEOUT)
        except urllib2.URLError:
            recent_failures += 1

            if recent_failures > THRESHOLD:
                alerts.harold.alert(tag, "[%s] %s is down" % (local_name, tag))
                recent_failures = THRESHOLD
        else:
            recent_failures = max(recent_failures - 1, 0)

        time.sleep(INTERVAL)
        alerts.harold.heartbeat("monitor_%s_%s" % (tag, local_name),
                                max(INTERVAL, TIMEOUT) * 2)


if __name__ == "__main__":
    alerts.init()
    url = sys.argv[1]
    monitor_site(url)
